from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.conf import settings

from RFQ_Mold.models import RFQ_Mold, RFQ_Mold_EditRequest
from RFQ_Mold.serializers import (
    RFQMoldCreateSerializer,
    RFQMoldDetailSerializer,
    RFQMoldListSerializer,
    MoldEditRequestCreateSerializer,
)
from RFQ_Trimming.models import RFQ_Trimming, RFQ_Trimming_EditRequest
from RFQ_Trimming.serializers import (
    RFQTrimmingCreateSerializer,
    RFQTrimmingDetailSerializer,
    RFQTrimmingListSerializer,
    TrimmingEditRequestCreateSerializer,
)

from notificaciones import tasks as notif_tasks
from notificaciones.services import ROL_COMERCIALIZACION

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_tipo(request):
    return request.query_params.get('tipo', '').lower()

def _tipo_invalido():
    return Response(
        {'detail': "El parámetro 'tipo' es requerido y debe ser 'mold' o 'trimming'."},
        status=status.HTTP_400_BAD_REQUEST,
    )

_TIPO_PARAM = OpenApiParameter(
    name='tipo',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    enum=['mold', 'trimming'],
    description="Tipo de RFQ: 'mold' o 'trimming'",
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CREAR RFQ
# ─────────────────────────────────────────────────────────────────────────────

class RFQCrearView(APIView):
    """
    POST /api_industrializacion/v1/rfq/?tipo=mold|trimming
    Crea un nuevo RFQ del tipo indicado.
    Acepta archivos opcionales bajo el key 'archivos' (multipart/form-data).
    El campo created_by se asigna automáticamente.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, JSONParser]

    @extend_schema(
        summary="Crear RFQ",
        description="""
            Crea un nuevo RFQ de tipo mold o trimming según el parámetro 'tipo'.
            Enviar como multipart/form-data si se incluyen archivos adjuntos.
            El status inicial debe ser En_Ind.
            Requiere autenticación.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            201: inline_serializer(
                name='RFQCrearResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='RFQCrearBadRequest',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            SerializerClass = RFQMoldCreateSerializer
        else:
            SerializerClass = RFQTrimmingCreateSerializer

        archivos   = request.FILES.getlist('archivos')
        serializer = SerializerClass(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user, archivos=archivos)

        return Response(
            {'detail': f'RFQ {tipo.capitalize()} creado correctamente.'},
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. EDITAR RFQ (solo mientras está en En_Ind)
# ─────────────────────────────────────────────────────────────────────────────

class RFQEditarView(APIView):
    """
    PATCH /api_industrializacion/v1/rfq/<id>/?tipo=mold|trimming
    Edita un RFQ existente. Solo permitido mientras el status sea En_Ind.
    Si el RFQ ya está en En_Com o En_Pro la edición es rechazada.
    Para desbloquearlo debe tramitarse una solicitud de edición aprobada.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, JSONParser]

    @extend_schema(
        summary="Editar RFQ (solo en En_Ind)",
        description="""
            Actualiza los campos de un RFQ. Solo se permite si el RFQ está en
            status En_Ind. Si está en En_Com o En_Pro se retorna 403.
            Requiere autenticación.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            200: inline_serializer(
                name='RFQEditarResponse',
                fields={'detail': serializers.CharField()}
            ),
            403: inline_serializer(
                name='RFQEditarForbidden',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='RFQEditarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def patch(self, request, pk):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                rfq = RFQ_Mold.objects.get(pk=pk, logical_delete=False)
            except RFQ_Mold.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Mold no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.status != RFQ_Mold.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ ya fue enviado y no puede editarse directamente. '
                               'Solicita una edición a Comercialización.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            archivos   = request.FILES.getlist('archivos')
            serializer = RFQMoldCreateSerializer(rfq, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(archivos=archivos)

        else:
            try:
                rfq = RFQ_Trimming.objects.get(pk=pk, logical_delete=False)
            except RFQ_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Trimming no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.status != RFQ_Trimming.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ ya fue enviado y no puede editarse directamente. '
                               'Solicita una edición a Comercialización.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            archivos   = request.FILES.getlist('archivos')
            serializer = RFQTrimmingCreateSerializer(rfq, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(archivos=archivos)

        return Response(
            {'detail': f'RFQ {tipo.capitalize()} actualizado correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENVIAR RFQ A COMERCIALIZACIÓN (En_Ind → En_Com)
# ─────────────────────────────────────────────────────────────────────────────

class RFQEnviarAComercializacionView(APIView):
    """
    POST /api_industrializacion/v1/rfq/<id>/enviar/?tipo=mold|trimming
    Cambia el status del RFQ de En_Ind a En_Com.
    Solo se permite si el RFQ está actualmente en En_Ind.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Enviar RFQ a Comercialización",
        description="""
            Cambia el status del RFQ de En_Ind a En_Com (submit to purchasing).
            Solo se permite si el RFQ está en En_Ind.
            Requiere autenticación.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            200: inline_serializer(
                name='RFQEnviarResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='RFQEnviarBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='RFQEnviarNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request, pk):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            try:
                rfq = RFQ_Mold.objects.get(pk=pk, logical_delete=False)
            except RFQ_Mold.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Mold no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.status != RFQ_Mold.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ solo puede enviarse a Comercialización desde el status En_Ind.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not rfq.archivos.exists():
                return Response(
                    {'detail': 'El RFQ debe tener al menos un archivo adjunto antes de enviarse.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rfq.status = RFQ_Mold.Status.COMERCIALIZACION
            rfq.save(update_fields=['status'])

        else:
            try:
                rfq = RFQ_Trimming.objects.get(pk=pk, logical_delete=False)
            except RFQ_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'RFQ Trimming no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if rfq.status != RFQ_Trimming.Status.INDUSTRIALIZACION:
                return Response(
                    {'detail': 'El RFQ solo puede enviarse a Comercialización desde el status En_Ind.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not rfq.archivos.exists():
                return Response(
                    {'detail': 'El RFQ debe tener al menos un archivo adjunto antes de enviarse.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rfq.status = RFQ_Trimming.Status.COMERCIALIZACION
            rfq.save(update_fields=['status'])

        return Response(
            {'detail': f'RFQ {tipo.capitalize()} enviado a Comercialización correctamente.'},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. SOLICITAR EDICIÓN (pide regresar de En_Com a En_Ind)
# ─────────────────────────────────────────────────────────────────────────────

class RFQSolicitarEdicionView(APIView):
    """
    POST /api_industrializacion/v1/edit-requests/?tipo=mold|trimming
    Crea una solicitud para regresar el RFQ de En_Com a En_Ind.
    Solo válido si el RFQ está en En_Com y no hay otra solicitud Pendiente.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Solicitar edición de RFQ (En_Com → En_Ind)",
        description="""
            Crea una solicitud para que Comercialización regrese el RFQ a En_Ind.
            El RFQ debe estar en En_Com y no puede haber una solicitud Pendiente activa.
            Requiere autenticación.
        """,
        parameters=[_TIPO_PARAM],
        responses={
            201: inline_serializer(
                name='SolicitarEdicionResponse',
                fields={'detail': serializers.CharField()}
            ),
            400: inline_serializer(
                name='SolicitarEdicionBadRequest',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def post(self, request):
        tipo = _get_tipo(request)
        if tipo not in ('mold', 'trimming'):
            return _tipo_invalido()

        if tipo == 'mold':
            serializer = MoldEditRequestCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(requested_by=request.user)
            if settings.NOTIFICATIONS_ENABLED:
                notif_tasks.notificar_modificacion_rfq.delay(
                    instance.rfq_mold.id, 'mold', request.user.id, [ROL_COMERCIALIZACION]
                )
        else:
            serializer = TrimmingEditRequestCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(requested_by=request.user)
            if settings.NOTIFICATIONS_ENABLED:
                notif_tasks.notificar_modificacion_rfq.delay(
                    instance.rfq_trimming.id, 'trimming', request.user.id, [ROL_COMERCIALIZACION]
                )

        return Response(
            {'detail': 'Solicitud de edición enviada correctamente.'},
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. LISTADO UNIFICADO DE RFQs PARA INDUSTRIALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────

class RFQListIndustrializacionView(APIView):
    """
    GET /api_industrializacion/v1/rfqs/
    Lista todos los RFQs (mold y trimming) con la siguiente regla de visibilidad:
      - Borradores (En_Ind): solo los creados por el usuario autenticado.
      - En_Com, En_Pro, complete: todos los usuarios.
    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listado de RFQs (Industrialización)",
        description="""
            Devuelve todos los RFQs activos de tipo Mold y Trimming.

            Regla de visibilidad:
            - **En_Ind (borradores):** solo los del usuario autenticado.
            - **En_Com, En_Pro, complete:** todos los usuarios.

            Requiere autenticación.
        """,
        responses={
            200: inline_serializer(
                name='RFQListIndustrializacionResponse',
                fields={
                    'mold':     RFQMoldListSerializer(many=True),
                    'trimming': RFQTrimmingListSerializer(many=True),
                }
            )
        },
    )
    def get(self, request):
        user = request.user

        from django.db.models import Q
        molds = RFQ_Mold.objects.filter(logical_delete=False).filter(
            Q(status=RFQ_Mold.Status.INDUSTRIALIZACION, created_by=user) |
            ~Q(status=RFQ_Mold.Status.INDUSTRIALIZACION)
        ).select_related('created_by').order_by('-created_date')

        trimmings = RFQ_Trimming.objects.filter(logical_delete=False).filter(
            Q(status=RFQ_Trimming.Status.INDUSTRIALIZACION, created_by=user) |
            ~Q(status=RFQ_Trimming.Status.INDUSTRIALIZACION)
        ).select_related('created_by').order_by('-created_date')

        return Response({
            'mold':     RFQMoldListSerializer(molds, many=True).data,
            'trimming': RFQTrimmingListSerializer(trimmings, many=True).data,
        })
