from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from users.permissions import IsProveedor, IsComercializacionUser
from .models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
    SolicitudExtensionMold,
    SolicitudExtensionTrimming,
)
from .serializers import (
    AsignacionMoldProveedorSerializer,
    AsignacionTrimmingProveedorSerializer,
    CostBreakdownMoldCreateSerializer,
    CostBreakdownTrimmingCreateSerializer,
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
    ...
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Mis asignaciones",
        description="""
            Devuelve todas las asignaciones activas del proveedor autenticado
            separadas en dos listas: mold y trimming.
            Requiere role='Pro'.
        """,
        responses={
            200: inline_serializer(
                name='AsignacionesResponse',
                fields={
                    'mold':     AsignacionMoldProveedorSerializer(many=True),
                    'trimming': AsignacionTrimmingProveedorSerializer(many=True),
                }
            )
        }
    )
    def get(self, request):
        proveedor             = request.user.proveedor
        asignaciones_mold     = Asignacion_Proveedor_Mold.objects.filter(id_Proveedor=proveedor, logical_delete=False)
        asignaciones_trimming = Asignacion_Proveedor_Trimming.objects.filter(id_Proveedor=proveedor, logical_delete=False)

        return Response({
            'mold':     AsignacionMoldProveedorSerializer(asignaciones_mold, many=True).data,
            'trimming': AsignacionTrimmingProveedorSerializer(asignaciones_trimming, many=True).data,
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


class AsignacionResponderView(APIView):
    """
    POST /asignaciones/responder/<id_asignacion>/?tipo=mold|trimming
    El proveedor envía su cost breakdown para una asignación.
    Solo se acepta una respuesta por asignación — si ya existe retorna 409.
    """
    permission_classes = [IsProveedor]

    @extend_schema(
        summary="Responder a una asignación (cost breakdown)",
        description="""
            El proveedor autenticado envía su cost breakdown completo para la
            asignación indicada. Solo se permite una respuesta por asignación.
            Requiere role='Pro' y que la asignación pertenezca al proveedor.
            Al guardar, la asignación queda marcada como is_answered=True.
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
        responses={
            201: inline_serializer(
                name='ResponderAsignacionResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='ResponderAsignacionBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='ResponderAsignacionNotFound',
                fields={'detail': serializers.CharField()}
            ),
            409: inline_serializer(
                name='ResponderAsignacionConflict',
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

            if hasattr(asignacion, 'cost_breakdown'):
                return Response(
                    {'detail': 'Esta asignación ya tiene una respuesta registrada.'},
                    status=status.HTTP_409_CONFLICT,
                )

            if asignacion.due_date < date.today():
                return Response(
                    {'detail': 'El plazo de esta asignación ha vencido. Solicita una extensión de tiempo.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = CostBreakdownMoldCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(id_asignacion=asignacion, last_edited_by=request.user)

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

            if hasattr(asignacion, 'cost_breakdown'):
                return Response(
                    {'detail': 'Esta asignación ya tiene una respuesta registrada.'},
                    status=status.HTTP_409_CONFLICT,
                )

            if asignacion.due_date < date.today():
                return Response(
                    {'detail': 'El plazo de esta asignación ha vencido. Solicita una extensión de tiempo.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = CostBreakdownTrimmingCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(id_asignacion=asignacion, last_edited_by=request.user)

        # Marcar la asignación como respondida
        asignacion.is_answered = True
        asignacion.save(update_fields=['is_answered'])

        return Response(
            {'detail': 'Respuesta registrada correctamente.'},
            status=status.HTTP_201_CREATED,
        )


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
            serializer.save(id_asignacion=asignacion)

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
            serializer.save(id_asignacion=asignacion)

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