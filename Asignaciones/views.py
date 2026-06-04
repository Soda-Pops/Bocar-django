from datetime import date

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from users.permissions import IsProveedor, IsComercializacionUser
from notificaciones import tasks as notif_tasks

from historial.models import RFQHistorial
from historial.services import registrar_historial
from .models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
    SolicitudExtensionMold,
    SolicitudExtensionTrimming,
)
from Prov_RFQ_Mold.models import Cost_Breakdown_Mold
from Prov_RFQ_Trimming.models import Cost_Breakdown_Trimming
from .serializers import (
    AsignacionMoldProveedorSerializer,
    AsignacionTrimmingProveedorSerializer,
    CostBreakdownMoldCreateSerializer,
    CostBreakdownMoldDetailSerializer,
    CostBreakdownMoldUpdateSerializer,
    CostBreakdownTrimmingCreateSerializer,
    CostBreakdownTrimmingDetailSerializer,
    CostBreakdownTrimmingUpdateSerializer,
    SolicitudExtensionMoldCreateSerializer,
    SolicitudExtensionTrimmingCreateSerializer,
    SolicitudExtensionMoldResolverSerializer,
    SolicitudExtensionTrimmingResolverSerializer,
)
from RFQ_Mold.serializers import RFQMoldDetailSerializer
from RFQ_Trimming.serializers import RFQTrimmingDetailSerializer

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class AsignacionesProveedorView(APIView):
    """
    GET /asignaciones/mis-asignaciones/
    Devuelve las asignaciones del proveedor autenticado separadas en
    pendientes (is_answered=False) y contestadas (is_answered=True),
    cada grupo dividido en mold y trimming.
    Incluye deadline dinámico e indicador de borrador guardado.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Mis asignaciones",
        description="""
            Devuelve las asignaciones del proveedor autenticado en dos grupos:
            - **pendientes**: aún no respondidas, con deadline dinámico.
            - **contestadas**: ya respondidas.
            Cada grupo separado en mold y trimming.
            Requiere role='Pro'.
        """,
        responses={
            200: inline_serializer(
                name='AsignacionesResponse',
                fields={
                    'pendientes': inline_serializer(
                        name='AsignacionesPendientes',
                        fields={
                            'mold':     AsignacionMoldProveedorSerializer(many=True),
                            'trimming': AsignacionTrimmingProveedorSerializer(many=True),
                        }
                    ),
                    'contestadas': inline_serializer(
                        name='AsignacionesContestadas',
                        fields={
                            'mold':     AsignacionMoldProveedorSerializer(many=True),
                            'trimming': AsignacionTrimmingProveedorSerializer(many=True),
                        }
                    ),
                }
            )
        }
    )
    def get(self, request):
        proveedor = request.user.proveedor
        base_mold = Asignacion_Proveedor_Mold.objects.filter(
            id_Proveedor=proveedor, logical_delete=False
        ).select_related('id_RFQ_Mold').prefetch_related('cost_breakdown')
        base_trimming = Asignacion_Proveedor_Trimming.objects.filter(
            id_Proveedor=proveedor, logical_delete=False
        ).select_related('id_RFQ_Trimming').prefetch_related('cost_breakdown')

        return Response({
            'pendientes': {
                'mold':     AsignacionMoldProveedorSerializer(
                                base_mold.filter(is_answered=False), many=True).data,
                'trimming': AsignacionTrimmingProveedorSerializer(
                                base_trimming.filter(is_answered=False), many=True).data,
            },
            'contestadas': {
                'mold':     AsignacionMoldProveedorSerializer(
                                base_mold.filter(is_answered=True), many=True).data,
                'trimming': AsignacionTrimmingProveedorSerializer(
                                base_trimming.filter(is_answered=True), many=True).data,
            },
        })


class AsignacionRFQDetalleView(APIView):
    """
    GET /asignaciones/detalle/<id_asignacion>/?tipo=mold|trimming
    Devuelve la información completa del RFQ asociado a una asignación.
    Solo el proveedor dueño de la asignación puede acceder.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Detalle de RFQ por asignación",
        description="""
            Devuelve la información completa del RFQ (mold o trimming) vinculado
            a la asignación indicada. Requiere role='Pro' y que la asignación
            pertenezca al proveedor autenticado.
        """,
        parameters=[
            OpenApiParameter(
                name='tipo',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                enum=['mold', 'trimming'],
                description="Tipo de RFQ: 'mold' o 'trimming'",
            )
        ],
        responses={200: None},
    )
    def get(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()

        if tipo not in ('mold', 'trimming'):
            return Response(
                {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        proveedor = request.user.proveedor

        if tipo == 'mold':
            try:
                asignacion = Asignacion_Proveedor_Mold.objects.get(
                    id=id_asignacion,
                    id_Proveedor=proveedor,
                    logical_delete=False,
                )
            except Asignacion_Proveedor_Mold.DoesNotExist:
                return Response(
                    {'detail': 'Asignación no encontrada o no pertenece a este proveedor.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = RFQMoldDetailSerializer(asignacion.id_RFQ_Mold)

        else:
            try:
                asignacion = Asignacion_Proveedor_Trimming.objects.get(
                    id=id_asignacion,
                    id_Proveedor=proveedor,
                    logical_delete=False,
                )
            except Asignacion_Proveedor_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'Asignación no encontrada o no pertenece a este proveedor.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = RFQTrimmingDetailSerializer(asignacion.id_RFQ_Trimming)

        return Response(serializer.data, status=status.HTTP_200_OK)


_TIPO_PARAM = OpenApiParameter(
    name='tipo', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
    required=True, enum=['mold', 'trimming'],
)

def _get_asignacion_mold(id_asignacion, proveedor):
    try:
        return Asignacion_Proveedor_Mold.objects.get(
            id=id_asignacion, id_Proveedor=proveedor, logical_delete=False
        )
    except Asignacion_Proveedor_Mold.DoesNotExist:
        return None

def _get_asignacion_trimming(id_asignacion, proveedor):
    try:
        return Asignacion_Proveedor_Trimming.objects.get(
            id=id_asignacion, id_Proveedor=proveedor, logical_delete=False
        )
    except Asignacion_Proveedor_Trimming.DoesNotExist:
        return None

_404_asignacion = {'detail': 'Asignación no encontrada o no pertenece a este proveedor.'}
_403_vencida    = {'detail': 'El plazo de esta asignación ha vencido. Solicita una extensión de tiempo.'}


class AsignacionResponderView(APIView):
    """
    POST /asignaciones/responder/<id_asignacion>/?tipo=mold|trimming
    Guarda el cost breakdown como BORRADOR (status=draft).
    No marca la asignación como respondida.
    Si ya existe un borrador retorna 409.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Guardar borrador de respuesta",
        description="""
            Crea un borrador del cost breakdown para la asignación.
            No marca la asignación como respondida.
            Para enviar definitivamente usar el endpoint /enviar/.
            Requiere role='Pro'.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            201: inline_serializer('BorradorCreadoResponse',   fields={'detail': serializers.CharField()}),
            400: inline_serializer('BorradorCreadoBadRequest', fields={'detail': serializers.CharField()}),
            403: inline_serializer('BorradorCreadoForbidden',  fields={'detail': serializers.CharField()}),
            404: inline_serializer('BorradorCreadoNotFound',   fields={'detail': serializers.CharField()}),
            409: inline_serializer('BorradorCreadoConflict',   fields={'detail': serializers.CharField()}),
        },
    )
    def post(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return Response({'detail': "El parámetro 'tipo' debe ser 'mold' o 'trimming'."}, status=status.HTTP_400_BAD_REQUEST)

        proveedor = request.user.proveedor

        if tipo == 'mold':
            asignacion = _get_asignacion_mold(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'Ya existe un borrador o respuesta para esta asignación.'}, status=status.HTTP_409_CONFLICT)
            if asignacion.due_date < date.today():
                return Response(_403_vencida, status=status.HTTP_403_FORBIDDEN)
            serializer = CostBreakdownMoldCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(id_asignacion=asignacion, last_edited_by=request.user, status='draft')
        else:
            asignacion = _get_asignacion_trimming(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'Ya existe un borrador o respuesta para esta asignación.'}, status=status.HTTP_409_CONFLICT)
            if asignacion.due_date < date.today():
                return Response(_403_vencida, status=status.HTTP_403_FORBIDDEN)
            serializer = CostBreakdownTrimmingCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(id_asignacion=asignacion, last_edited_by=request.user, status='draft')

        return Response({'detail': 'Borrador guardado correctamente.'}, status=status.HTTP_201_CREATED)


class AsignacionBorradorDetalleView(APIView):
    """
    GET /asignaciones/responder/<id_asignacion>/?tipo=mold|trimming
    Devuelve el borrador o respuesta enviada de una asignación.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Ver borrador o respuesta guardada",
        description="Devuelve el cost breakdown (borrador o enviado) de la asignación. Requiere role='Pro'.",
        parameters=[_TIPO_PARAM],
        responses={200: None, 404: inline_serializer('BorradorDetalleNotFound', fields={'detail': serializers.CharField()})},
    )
    def get(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return Response({'detail': "El parámetro 'tipo' debe ser 'mold' o 'trimming'."}, status=status.HTTP_400_BAD_REQUEST)

        proveedor = request.user.proveedor

        if tipo == 'mold':
            asignacion = _get_asignacion_mold(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para esta asignación.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(CostBreakdownMoldDetailSerializer(asignacion.cost_breakdown).data)
        else:
            asignacion = _get_asignacion_trimming(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para esta asignación.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(CostBreakdownTrimmingDetailSerializer(asignacion.cost_breakdown).data)


class AsignacionBorradorActualizarView(APIView):
    """
    PATCH /asignaciones/responder/<id_asignacion>/actualizar/?tipo=mold|trimming
    Actualiza el borrador. Solo si status=draft; rechaza si ya está submitted.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Actualizar borrador",
        description="Actualiza campos del borrador. Solo permitido si status='draft'. Requiere role='Pro'.",
        parameters=[_TIPO_PARAM],
        responses={
            200: inline_serializer('BorradorActualizadoResponse', fields={'detail': serializers.CharField()}),
            403: inline_serializer('BorradorActualizadoForbidden', fields={'detail': serializers.CharField()}),
            404: inline_serializer('BorradorActualizadoNotFound', fields={'detail': serializers.CharField()}),
        },
    )
    def patch(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return Response({'detail': "El parámetro 'tipo' debe ser 'mold' o 'trimming'."}, status=status.HTTP_400_BAD_REQUEST)

        proveedor = request.user.proveedor

        if tipo == 'mold':
            asignacion = _get_asignacion_mold(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para actualizar.'}, status=status.HTTP_404_NOT_FOUND)
            breakdown = asignacion.cost_breakdown
            if breakdown.status == Cost_Breakdown_Mold.Status.SUBMITTED:
                return Response({'detail': 'La respuesta ya fue enviada y no puede modificarse.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = CostBreakdownMoldUpdateSerializer(breakdown, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(last_edited_by=request.user)
        else:
            asignacion = _get_asignacion_trimming(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para actualizar.'}, status=status.HTTP_404_NOT_FOUND)
            breakdown = asignacion.cost_breakdown
            if breakdown.status == Cost_Breakdown_Trimming.Status.SUBMITTED:
                return Response({'detail': 'La respuesta ya fue enviada y no puede modificarse.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = CostBreakdownTrimmingUpdateSerializer(breakdown, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(last_edited_by=request.user)

        return Response({'detail': 'Borrador actualizado correctamente.'}, status=status.HTTP_200_OK)


class AsignacionEnviarRespuestaView(APIView):
    """
    POST /asignaciones/responder/<id_asignacion>/enviar/?tipo=mold|trimming
    Envía definitivamente el borrador (draft → submitted).
    Marca la asignación como is_answered=True.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Enviar respuesta definitiva",
        description="""
            Cambia el borrador de status draft a submitted y marca la asignación
            como respondida. No se puede revertir. Requiere role='Pro'.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            200: inline_serializer('EnviarRespuestaResponse',  fields={'detail': serializers.CharField()}),
            403: inline_serializer('EnviarRespuestaForbidden', fields={'detail': serializers.CharField()}),
            404: inline_serializer('EnviarRespuestaNotFound',  fields={'detail': serializers.CharField()}),
            409: inline_serializer('EnviarRespuestaConflict',  fields={'detail': serializers.CharField()}),
        },
    )
    def post(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in ('mold', 'trimming'):
            return Response({'detail': "El parámetro 'tipo' debe ser 'mold' o 'trimming'."}, status=status.HTTP_400_BAD_REQUEST)

        proveedor = request.user.proveedor

        if tipo == 'mold':
            asignacion = _get_asignacion_mold(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para enviar. Crea uno primero.'}, status=status.HTTP_404_NOT_FOUND)
            breakdown = asignacion.cost_breakdown
            if breakdown.status == Cost_Breakdown_Mold.Status.SUBMITTED:
                return Response({'detail': 'Esta respuesta ya fue enviada.'}, status=status.HTTP_409_CONFLICT)
            if asignacion.due_date < date.today():
                return Response(_403_vencida, status=status.HTTP_403_FORBIDDEN)
            breakdown.status = Cost_Breakdown_Mold.Status.SUBMITTED
            breakdown.last_edited_by = request.user
            breakdown.save(update_fields=['status', 'last_edited_by'])
        else:
            asignacion = _get_asignacion_trimming(id_asignacion, proveedor)
            if not asignacion:
                return Response(_404_asignacion, status=status.HTTP_404_NOT_FOUND)
            if not hasattr(asignacion, 'cost_breakdown'):
                return Response({'detail': 'No hay borrador para enviar. Crea uno primero.'}, status=status.HTTP_404_NOT_FOUND)
            breakdown = asignacion.cost_breakdown
            if breakdown.status == Cost_Breakdown_Trimming.Status.SUBMITTED:
                return Response({'detail': 'Esta respuesta ya fue enviada.'}, status=status.HTTP_409_CONFLICT)
            if asignacion.due_date < date.today():
                return Response(_403_vencida, status=status.HTTP_403_FORBIDDEN)
            breakdown.status = Cost_Breakdown_Trimming.Status.SUBMITTED
            breakdown.last_edited_by = request.user
            breakdown.save(update_fields=['status', 'last_edited_by'])

        asignacion.is_answered = True
        asignacion.save(update_fields=['is_answered'])

        rfq = asignacion.id_RFQ_Mold if tipo == 'mold' else asignacion.id_RFQ_Trimming

        registrar_historial(
            rfq_tipo = tipo,
            rfq_id   = rfq.id,
            evento   = RFQHistorial.Evento.COTIZACION_RECIBIDA,
            actor    = request.user,
            detalle  = {'proveedor': proveedor.company_name},
        )

        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_cotizacion_recibida.delay(rfq.id, tipo, request.user.id)

        return Response({'detail': 'Respuesta enviada correctamente.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUD DE EXTENSIÓN DE TIEMPO — CREAR (proveedor)
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionCreateView(APIView):
    """
    POST /asignaciones/extension/solicitar/<id_asignacion>/?tipo=mold|trimming
    El proveedor solicita más tiempo para contestar una asignación vencida.
    Solo puede haber una solicitud Pendiente por asignación a la vez.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Solicitar extensión de tiempo",
        description="""
            El proveedor solicita ampliar el plazo de una asignación.
            Solo se permite una solicitud pendiente por asignación.
            Requiere role='Pro' y que la asignación pertenezca al proveedor.
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
        responses={
            201: inline_serializer(
                name='ExtensionSolicitadaResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ExtensionSolicitadaBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='ExtensionSolicitadaNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request, id_asignacion):
        tipo = request.query_params.get('tipo', '').lower()

        if tipo not in ('mold', 'trimming'):
            return Response(
                {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        proveedor = request.user.proveedor

        if tipo == 'mold':
            try:
                asignacion = Asignacion_Proveedor_Mold.objects.get(
                    id=id_asignacion,
                    id_Proveedor=proveedor,
                    logical_delete=False,
                )
            except Asignacion_Proveedor_Mold.DoesNotExist:
                return Response(
                    {'detail': 'Asignación no encontrada o no pertenece a este proveedor.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SolicitudExtensionMoldCreateSerializer(
                data=request.data,
                context={'asignacion': asignacion},
            )
            serializer.is_valid(raise_exception=True)
            solicitud = serializer.save(id_asignacion=asignacion)
            rfq_id    = asignacion.id_RFQ_Mold_id

        else:
            try:
                asignacion = Asignacion_Proveedor_Trimming.objects.get(
                    id=id_asignacion,
                    id_Proveedor=proveedor,
                    logical_delete=False,
                )
            except Asignacion_Proveedor_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'Asignación no encontrada o no pertenece a este proveedor.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SolicitudExtensionTrimmingCreateSerializer(
                data=request.data,
                context={'asignacion': asignacion},
            )
            serializer.is_valid(raise_exception=True)
            solicitud = serializer.save(id_asignacion=asignacion)
            rfq_id    = asignacion.id_RFQ_Trimming_id

        registrar_historial(
            rfq_tipo = tipo,
            rfq_id   = rfq_id,
            evento   = RFQHistorial.Evento.EXTENSION_SOLICITADA,
            actor    = request.user,
            detalle  = {'nueva_fecha': str(solicitud.nueva_fecha)},
        )

        return Response(
            {'detail': 'Solicitud de extensión enviada correctamente.'},
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SOLICITUD DE EXTENSIÓN DE TIEMPO — RESOLVER (comercialización)
# ─────────────────────────────────────────────────────────────────────────────

class SolicitudExtensionResolverView(APIView):
    """
    PATCH /asignaciones/extension/resolver/<id_solicitud>/?tipo=mold|trimming
    Comercialización aprueba o rechaza una solicitud de extensión.
    Si se aprueba, el due_date de la asignación se actualiza.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Aprobar o rechazar solicitud de extensión",
        description="""
            Un usuario de Comercialización resuelve la solicitud de extensión
            de tiempo de un proveedor. Si se aprueba, el due_date de la asignación
            se actualiza a la nueva_fecha propuesta.
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
        responses={
            200: inline_serializer(
                name='ExtensionResueltaResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ExtensionResueltaBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='ExtensionResueltaNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, id_solicitud):
        tipo = request.query_params.get('tipo', '').lower()

        if tipo not in ('mold', 'trimming'):
            return Response(
                {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo == 'mold':
            try:
                solicitud = SolicitudExtensionMold.objects.get(id=id_solicitud)
            except SolicitudExtensionMold.DoesNotExist:
                return Response(
                    {'detail': 'Solicitud no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SolicitudExtensionMoldResolverSerializer(
                solicitud,
                data=request.data,
                partial=True,
                context={'request': request},
            )
        else:
            try:
                solicitud = SolicitudExtensionTrimming.objects.get(id=id_solicitud)
            except SolicitudExtensionTrimming.DoesNotExist:
                return Response(
                    {'detail': 'Solicitud no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = SolicitudExtensionTrimmingResolverSerializer(
                solicitud,
                data=request.data,
                partial=True,
                context={'request': request},
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        accion = 'aprobada' if serializer.instance.status == 'Aprobada' else 'rechazada'
        return Response(
            {'detail': f'Solicitud de extensión {accion} correctamente.'},
            status=status.HTTP_200_OK,
        )