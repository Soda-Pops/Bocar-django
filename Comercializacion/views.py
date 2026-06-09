from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from users.permissions import IsComercializacionUser, IsComercializacionAdmin
from RFQ_Mold.models import RFQ_Mold, RFQ_Mold_EditRequest
from Prov_RFQ_Mold.models import Cost_Breakdown_Mold
from Prov_RFQ_Trimming.models import Cost_Breakdown_Trimming
from RFQ_Mold.serializers import MoldEditRequestApproveSerializer, MoldEditRequestListSerializer
from RFQ_Trimming.models import RFQ_Trimming, RFQ_Trimming_EditRequest
from RFQ_Trimming.serializers import TrimmingEditRequestApproveSerializer, TrimmingEditRequestListSerializer
from Proveedores.models import Proveedor
from Asignaciones.models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
    SolicitudExtensionMold,
    SolicitudExtensionTrimming,
)
from Asignaciones.serializers import (
    SolicitudExtensionMoldListSerializer,
    SolicitudExtensionTrimmingListSerializer,
    SolicitudExtensionMoldResolverSerializer,
    SolicitudExtensionTrimmingResolverSerializer,
)
from .serializers import (
    RFQMoldComercializacionSerializer,
    RFQTrimmingComercializacionSerializer,
    CrearAsignacionesSerializer,
)
from django.conf import settings
from notificaciones import tasks as notif_tasks
from notificaciones.services import ROL_INDUSTRIALIZACION

from django.db import transaction

from historial.models import RFQHistorial
from historial.services import registrar_historial

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


_TIPO_PARAM = OpenApiParameter(
    name='tipo',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    enum=['mold', 'trimming'],
)

def _tipo_invalido():
    return Response(
        {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
        status=status.HTTP_400_BAD_REQUEST,
    )


class RFQListComercializacionView(APIView):
    """
    GET /api_comercializacion/v1/rfqs/
    Lista todos los RFQ activos (Mold y Trimming) para usuarios de Comercialización.
    Incluye: id, nombre de pieza, status, tipo, deadline dinámico,
             fecha de creación (dd-mm-aa), creador y progreso de proveedores.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Listado de todos los RFQs (Comercialización)",
        description="""
            Devuelve todos los RFQ activos de tipo Mold y Trimming combinados,
            ordenados por fecha de creación descendente.

            - **deadline**: días restantes ("X días"), horas si queda menos de 24h
              ("Xh Ym"), o "Vencido" si ya pasó la fecha.
            - **progreso_proveedores**: "Sin proveedores asignados" si no hay ninguno,
              "X/Y contestados" si hay respuestas parciales, "Completo" si todos
              respondieron.

            Requiere role='Com'.
        """,
        responses={
            200: inline_serializer(
                name='RFQListComercializacionResponse',
                fields={
                    'mold':     RFQMoldComercializacionSerializer(many=True),
                    'trimming': RFQTrimmingComercializacionSerializer(many=True),
                }
            )
        },
    )
    def get(self, request):
        molds = RFQ_Mold.objects.filter(
            logical_delete=False
        ).select_related('created_by').prefetch_related('asignaciones').order_by('-created_date')

        trimmings = RFQ_Trimming.objects.filter(
            logical_delete=False
        ).select_related('created_by').prefetch_related('asignaciones').order_by('-created_date')

        return Response({
            'mold':     RFQMoldComercializacionSerializer(molds, many=True).data,
            'trimming': RFQTrimmingComercializacionSerializer(trimmings, many=True).data,
        }, status=status.HTTP_200_OK)


class CrearAsignacionesView(APIView):
    """
    POST /api_comercializacion/v1/asignaciones/crear/?tipo=mold|trimming
    Asigna uno o varios proveedores a un RFQ. Si algún proveedor ya tiene
    asignación activa para ese RFQ, se omite sin error.
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Crear asignaciones de proveedores a un RFQ",
        description="""
            Asigna una lista de proveedores a un RFQ específico (mold o trimming).
            Los proveedores que ya tengan asignación activa para ese RFQ son omitidos
            silenciosamente. Puede llamarse múltiples veces para agregar más proveedores.
            Requiere role='Com'.
        """,
        parameters=[
            OpenApiParameter(
                name='tipo',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=['mold', 'trimming'],
            )
        ],
        request=CrearAsignacionesSerializer,
        responses={
            200: inline_serializer(
                name='CrearAsignacionesResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='CrearAsignacionesBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='CrearAsignacionesNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request):
        tipo = request.query_params.get('tipo', '').lower()

        if tipo not in ('mold', 'trimming'):
            return Response(
                {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CrearAsignacionesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_rfq      = serializer.validated_data['id_rfq']
        due_date    = serializer.validated_data['due_date']
        proveedores = serializer.validated_data['proveedores']
        paso_a_pro  = False

        with transaction.atomic():
            # Verificar que el RFQ existe
            if tipo == 'mold':
                try:
                    rfq = RFQ_Mold.objects.select_for_update().get(id=id_rfq, logical_delete=False)
                except RFQ_Mold.DoesNotExist:
                    return Response(
                        {'detail': 'RFQ Mold no encontrado.'},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for id_proveedor in proveedores:
                    try:
                        proveedor = Proveedor.objects.get(id=id_proveedor)
                    except Proveedor.DoesNotExist:
                        continue  # proveedor inválido, se omite

                    # Si ya existe asignación activa para este par rfq+proveedor, omitir
                    ya_existe = Asignacion_Proveedor_Mold.objects.filter(
                        id_RFQ_Mold=rfq,
                        id_Proveedor=proveedor,
                        logical_delete=False,
                    ).exists()

                    if not ya_existe:
                        Asignacion_Proveedor_Mold.objects.create(
                            id_RFQ_Mold=rfq,
                            id_Proveedor=proveedor,
                            id_user_comercializacion=request.user,
                            due_date=due_date,
                        )

                # Mover el RFQ a En_Pro si aún no lo está
                if rfq.status != RFQ_Mold.Status.PROVEEDOR:
                    rfq.status = RFQ_Mold.Status.PROVEEDOR
                    rfq.save(update_fields=['status'])
                    paso_a_pro = True

            else:
                try:
                    rfq = RFQ_Trimming.objects.select_for_update().get(id=id_rfq, logical_delete=False)
                except RFQ_Trimming.DoesNotExist:
                    return Response(
                        {'detail': 'RFQ Trimming no encontrado.'},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for id_proveedor in proveedores:
                    try:
                        proveedor = Proveedor.objects.get(id=id_proveedor)
                    except Proveedor.DoesNotExist:
                        continue

                    ya_existe = Asignacion_Proveedor_Trimming.objects.filter(
                        id_RFQ_Trimming=rfq,
                        id_Proveedor=proveedor,
                        logical_delete=False,
                    ).exists()

                    if not ya_existe:
                        Asignacion_Proveedor_Trimming.objects.create(
                            id_RFQ_Trimming=rfq,
                            id_Proveedor=proveedor,
                            id_user_comercializacion=request.user,
                            due_date=due_date,
                        )

                # Mover el RFQ a En_Pro si aún no lo está
                if rfq.status != RFQ_Trimming.Status.PROVEEDOR:
                    rfq.status = RFQ_Trimming.Status.PROVEEDOR
                    rfq.save(update_fields=['status'])
                    paso_a_pro = True

            # Historial: envío a proveedores (solo en la transición) + asignación
            if paso_a_pro:
                registrar_historial(
                    rfq_tipo        = tipo,
                    rfq_id          = rfq.id,
                    evento          = RFQHistorial.Evento.ENVIO_PROVEEDORES,
                    actor           = request.user,
                    status_anterior = 'En_Com',
                    status_nuevo    = 'En_Pro',
                )
            registrar_historial(
                rfq_tipo = tipo,
                rfq_id   = rfq.id,
                evento   = RFQHistorial.Evento.ASIGNACION_PROVEEDORES,
                actor    = request.user,
                detalle  = {'proveedores': proveedores, 'due_date': str(due_date)},
            )

            if settings.NOTIFICATIONS_ENABLED:
                transaction.on_commit(
                    lambda: notif_tasks.notificar_proveedores.delay(rfq.id, tipo)
                )

        return Response(
            {'detail': 'Asignaciones procesadas correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# APROBAR SOLICITUD DE EDICIÓN
# ─────────────────────────────────────────────────────────────────────────────

class EditRequestAprobarView(APIView):
    """
    PATCH /api_comercializacion/v1/edit-requests/<id>/aprobar/?tipo=mold|trimming
    Aprueba una solicitud de edición pendiente.
    Regresa el RFQ a En_Ind para que Industrialización pueda editarlo.
    Requiere role=Com.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Aprobar solicitud de edición",
        description="""
            Aprueba una solicitud de edición pendiente. El RFQ vuelve a En_Ind.
            Requiere role='Com'.
            No requiere cuerpo en el request.
        """,
        parameters=[_TIPO_PARAM],
        request=None,
        responses={
            200: inline_serializer(
                name='EditRequestAprobarResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='EditRequestAprobarBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='EditRequestAprobarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, pk):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                edit_request = RFQ_Mold_EditRequest.objects.get(pk=pk)
            except RFQ_Mold_EditRequest.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = MoldEditRequestApproveSerializer(
                edit_request, data=request.data, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                serializer.save()
                if settings.NOTIFICATIONS_ENABLED:
                    transaction.on_commit(
                        lambda: notif_tasks.notificar_modificacion_rfq.delay(
                            edit_request.rfq_mold.id, 'mold', request.user.id, [ROL_INDUSTRIALIZACION]
                        )
                    )
        else:
            try:
                edit_request = RFQ_Trimming_EditRequest.objects.get(pk=pk)
            except RFQ_Trimming_EditRequest.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = TrimmingEditRequestApproveSerializer(
                edit_request, data=request.data, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                serializer.save()
                if settings.NOTIFICATIONS_ENABLED:
                    transaction.on_commit(
                        lambda: notif_tasks.notificar_modificacion_rfq.delay(
                            edit_request.rfq_trimming.id, 'trimming', request.user.id, [ROL_INDUSTRIALIZACION]
                        )
                    )

        return Response(
            {'detail': 'Solicitud de edición aprobada. El RFQ ha vuelto a En_Ind.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# RECHAZAR SOLICITUD DE EDICIÓN
# ─────────────────────────────────────────────────────────────────────────────

class EditRequestRechazarView(APIView):
    """
    PATCH /api_comercializacion/v1/edit-requests/<id>/rechazar/?tipo=mold|trimming
    Rechaza una solicitud de edición pendiente.
    El RFQ permanece en su status actual (En_Com).
    Requiere role=Com.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Rechazar solicitud de edición",
        description="""
            Rechaza una solicitud de edición pendiente. El RFQ permanece en En_Com.
            Se registra el motivo del rechazo, el revisor y el timestamp.
            Requiere role='Com'.
            No requiere cuerpo en el request.
        """,
        parameters=[_TIPO_PARAM],
        request=None,
        responses={
            200: inline_serializer(
                name='EditRequestRechazarResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='EditRequestRechazarBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='EditRequestRechazarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, pk):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                edit_request = RFQ_Mold_EditRequest.objects.get(pk=pk)
            except RFQ_Mold_EditRequest.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            if edit_request.status != 'Pendiente':
                return Response(
                    {'detail': 'Esta solicitud ya fue resuelta.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            edit_request.status      = RFQ_Mold_EditRequest.EditStatus.RECHAZADA
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()

        else:
            try:
                edit_request = RFQ_Trimming_EditRequest.objects.get(pk=pk)
            except RFQ_Trimming_EditRequest.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

            if edit_request.status != 'Pendiente':
                return Response(
                    {'detail': 'Esta solicitud ya fue resuelta.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            edit_request.status      = RFQ_Trimming_EditRequest.EditStatus.RECHAZADA
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()

        rfq_id = edit_request.rfq_mold_id if tipo == 'mold' else edit_request.rfq_trimming_id
        registrar_historial(
            rfq_tipo = tipo,
            rfq_id   = rfq_id,
            evento   = RFQHistorial.Evento.EDICION_RECHAZADA,
            actor    = request.user,
        )

        return Response(
            {'detail': 'Solicitud de edición rechazada. El RFQ permanece en su status actual.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# LISTADO UNIFICADO DE SOLICITUDES PENDIENTES
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudesPendientesView(APIView):
    """
    GET /api_comercializacion/v1/solicitudes/
    Devuelve en un solo objeto dos listas:
      - solicitudes_edicion: de Industrialización hacia Comercialización (Pendientes).
      - solicitudes_extension: de Proveedores hacia Comercialización (Pendientes).
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Solicitudes pendientes (edición + extensión)",
        description="""
            Devuelve todas las solicitudes pendientes que requieren atención de Comercialización:
            - **solicitudes_edicion**: solicitudes de Industrialización para regresar un RFQ a En_Ind.
            - **solicitudes_extension**: solicitudes de Proveedores para ampliar su plazo de respuesta.
            Ambas listas separadas por tipo (mold / trimming).
            Requiere role='Com'.
        """,
        responses={
            200: inline_serializer(
                name='SolicitudesPendientesResponse',
                fields={
                    'solicitudes_edicion': inline_serializer(
                        name='SolicitudesEdicion',
                        fields={
                            'mold':     MoldEditRequestListSerializer(many=True),
                            'trimming': TrimmingEditRequestListSerializer(many=True),
                        }
                    ),
                    'solicitudes_extension': inline_serializer(
                        name='SolicitudesExtension',
                        fields={
                            'mold':     SolicitudExtensionMoldListSerializer(many=True),
                            'trimming': SolicitudExtensionTrimmingListSerializer(many=True),
                        }
                    ),
                }
            )
        },
    )
    def get(self, request):
        edit_mold     = RFQ_Mold_EditRequest.objects.filter(status='Pendiente').select_related(
            'rfq_mold', 'requested_by'
        )
        edit_trimming = RFQ_Trimming_EditRequest.objects.filter(status='Pendiente').select_related(
            'rfq_trimming', 'requested_by'
        )
        ext_mold      = SolicitudExtensionMold.objects.filter(status='Pendiente').select_related(
            'id_asignacion__id_Proveedor', 'id_asignacion__id_RFQ_Mold'
        )
        ext_trimming  = SolicitudExtensionTrimming.objects.filter(status='Pendiente').select_related(
            'id_asignacion__id_Proveedor', 'id_asignacion__id_RFQ_Trimming'
        )

        return Response({
            'solicitudes_edicion': {
                'mold':     MoldEditRequestListSerializer(edit_mold, many=True).data,
                'trimming': TrimmingEditRequestListSerializer(edit_trimming, many=True).data,
            },
            'solicitudes_extension': {
                'mold':     SolicitudExtensionMoldListSerializer(ext_mold, many=True).data,
                'trimming': SolicitudExtensionTrimmingListSerializer(ext_trimming, many=True).data,
            },
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# RESOLVER EXTENSIÓN DE TIEMPO (movido desde Asignaciones)
# ─────────────────────────────────────────────────────────────────────────────

class ExtensionTiempoResolverView(APIView):
    """
    PATCH /api_comercializacion/v1/extension/<id>/resolver/?tipo=mold|trimming
    Aprueba o rechaza una solicitud de extensión de tiempo de un proveedor.
    Si se aprueba, actualiza el due_date de la asignación del proveedor.
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Resolver solicitud de extensión de tiempo",
        description="""
            Aprueba o rechaza la solicitud de extensión de plazo de un proveedor.
            Si se aprueba, el due_date de la asignación del proveedor se actualiza
            a la nueva fecha propuesta. El due_date del RFQ no se modifica.
            Requiere role='Com'.
        """,
        parameters=[_TIPO_PARAM],
        request=SolicitudExtensionMoldResolverSerializer,
        responses={
            200: inline_serializer(
                name='ExtensionResolverResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ExtensionResolverBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='ExtensionResolverNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, pk):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                solicitud = SolicitudExtensionMold.objects.get(pk=pk)
            except SolicitudExtensionMold.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SolicitudExtensionMoldResolverSerializer(
                solicitud, data=request.data, partial=True, context={'request': request}
            )
        else:
            try:
                solicitud = SolicitudExtensionTrimming.objects.get(pk=pk)
            except SolicitudExtensionTrimming.DoesNotExist:
                return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SolicitudExtensionTrimmingResolverSerializer(
                solicitud, data=request.data, partial=True, context={'request': request}
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        accion = 'aprobada' if serializer.instance.status == 'Aprobada' else 'rechazada'
        return Response(
            {'detail': f'Solicitud de extensión {accion} correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# COMPARATIVA DE PRECIOS POR PROVEEDOR
# ─────────────────────────────────────────────────────────────────────────────

_PRECIO_CAMPOS = (
    'accs_grand_total_sum',
    'mat_grand_total_sum',
    'grand_total_sum',
    'corr_grand_total_sum',
    'log_grand_total_sum',
)


class ComparativaProveedoresView(APIView):
    """
    GET /api_comercializacion/v1/rfq/<rfq_id>/comparativa/?tipo=mold|trimming
    Devuelve la lista de proveedores que ya respondieron al RFQ con su desglose
    de precios y el precio total calculado.
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Comparativa de precios por proveedor",
        description="""
            Devuelve todos los proveedores que ya enviaron su cotización (`is_answered=True`)
            para el RFQ indicado. Por cada uno incluye el desglose de cinco totales y
            el `precio_total` calculado como su suma.
            Requiere `role='Com'`.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            200: inline_serializer(
                name='ComparativaProveedorItem',
                many=True,
                fields={
                    'usuario_id':            serializers.IntegerField(),
                    'nombre_empresa':        serializers.CharField(),
                    'accs_grand_total_sum':  serializers.FloatField(),
                    'mat_grand_total_sum':   serializers.FloatField(),
                    'grand_total_sum':       serializers.FloatField(),
                    'corr_grand_total_sum':  serializers.FloatField(),
                    'log_grand_total_sum':   serializers.FloatField(),
                    'precio_total':          serializers.FloatField(),
                },
            ),
            400: inline_serializer(
                name='ComparativaBadRequest',
                fields={'detail': serializers.CharField()},
            ),
            404: inline_serializer(
                name='ComparativaNotFound',
                fields={'detail': serializers.CharField()},
            ),
        },
    )
    def get(self, request, rfq_id):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            if not RFQ_Mold.objects.filter(pk=rfq_id, logical_delete=False).exists():
                return Response({'detail': 'RFQ no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            asignaciones = (
                Asignacion_Proveedor_Mold.objects
                .filter(id_RFQ_Mold=rfq_id, is_answered=True, logical_delete=False)
                .select_related('id_Proveedor__id_account', 'cost_breakdown')
            )
        else:
            if not RFQ_Trimming.objects.filter(pk=rfq_id, logical_delete=False).exists():
                return Response({'detail': 'RFQ no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            asignaciones = (
                Asignacion_Proveedor_Trimming.objects
                .filter(id_RFQ_Trimming=rfq_id, is_answered=True, logical_delete=False)
                .select_related('id_Proveedor__id_account', 'cost_breakdown')
            )

        resultado = []
        for asignacion in asignaciones:
            try:
                cb = asignacion.cost_breakdown
            except (Cost_Breakdown_Mold.DoesNotExist, Cost_Breakdown_Trimming.DoesNotExist):
                continue

            proveedor = asignacion.id_Proveedor
            usuario   = proveedor.id_account

            totales = {campo: getattr(cb, campo, 0.0) for campo in _PRECIO_CAMPOS}
            resultado.append({
                'usuario_id':           usuario.id,
                'nombre_empresa':       proveedor.company_name,
                **totales,
                'precio_total':         sum(totales.values()),
            })

        return Response(resultado, status=status.HTTP_200_OK)
