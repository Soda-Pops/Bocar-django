from rest_framework import generics, status, serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from .models import RFQ_Trimming, RFQ_Trimming_EditRequest
from .serializers import RFQTrimmingCreateSerializer, RFQTrimmingDetailSerializer, RFQTrimmingListSerializer

from users.permissions import IsAdminUser, IsComercializacionAdmin, IsIndustrializacionUser

from notificaciones import tasks as notif_tasks
from django.conf import settings

from historial.models import RFQHistorial
from historial.services import registrar_historial
from drf_spectacular.utils import extend_schema, inline_serializer


class RFQTrimmingListCreateView(generics.ListAPIView):
    """
    GET /rfq-trimmings/
    Devuelve la lista de RFQ Trimmings activos (logical_delete=False) con campos resumidos.
    Endpoint deprecado — usar /api_industrializacion/v1/ para crear y gestionar RFQs.
    Requiere role='Ind'.
    """
    permission_classes = [IsIndustrializacionUser]
    serializer_class   = RFQTrimmingListSerializer

    @extend_schema(
        tags=['RFQ Trimming'],
        summary='Listar RFQ Trimmings (deprecado)',
        description=(
            'Devuelve todos los RFQ Trimmings activos (`logical_delete=False`) con campos resumidos.\n\n'
            '**Deprecado** — usar `/api_industrializacion/v1/` para el flujo completo.\n\n'
            'Requiere `role=Ind`.'
        ),
        responses={200: RFQTrimmingListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return RFQ_Trimming.objects.filter(logical_delete=False)


@extend_schema(
    tags=['RFQ Trimming'],
    summary='Detalle de RFQ Trimming',
    description=(
        'Devuelve todos los campos del RFQ Trimming por ID, incluyendo archivos adjuntos '
        'y el nombre del creador (`created_by_name`).\n\n'
        'Industrialización puede consultar RFQs activos. Comercialización solo puede '
        'consultar RFQs activos en `En_Com` o `En_Pro`.'
    ),
    responses={
        200: RFQTrimmingDetailSerializer,
        404: inline_serializer(
            name='RFQTrimmingDetailNotFound',
            fields={'detail': drf_serializers.CharField()},
        ),
    },
)
class RFQTrimmingDetailView(generics.RetrieveAPIView):
    """
    GET /rfq-trimmings/<id>/
    Devuelve todos los campos del RFQ Trimming incluyendo archivos adjuntos y nombre del creador.
    Industrialización ve RFQs activos. Comercialización solo ve RFQs activos en En_Com o En_Pro.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = RFQTrimmingDetailSerializer

    def get_queryset(self):
        queryset = RFQ_Trimming.objects.filter(logical_delete=False)
        role = getattr(self.request.user, 'role', None)

        if role == 'Ind':
            return queryset
        if role == 'Com':
            return queryset.filter(
                status__in=[
                    RFQ_Trimming.Status.COMERCIALIZACION,
                    RFQ_Trimming.Status.PROVEEDOR,
                ]
            )
        return queryset.none()


class RFQTrimmingLogicalDeleteView(UpdateAPIView):
    """
    PATCH /rfq-trimmings/<id>/delete/
    Marca el RFQ Trimming como eliminado (logical_delete=True).
    El registro NO se borra físicamente de la base de datos.
    Retorna error si el registro ya estaba marcado como eliminado.
    Requiere: is_admin=True y role='Com'.
    """
    permission_classes = [IsComercializacionAdmin]
    queryset           = RFQ_Trimming.objects.all()
    http_method_names  = ['patch']
    serializer_class   = drf_serializers.Serializer  # requerido por UpdateAPIView; no se usa en partial_update

    @extend_schema(
        tags=['RFQ Trimming'],
        summary='Borrado lógico de RFQ Trimming',
        description=(
            'Marca el RFQ Trimming como eliminado (`logical_delete=True`). '
            'El registro **no** se borra físicamente de la base de datos.\n\n'
            'Retorna 400 si el registro ya tenía `logical_delete=True`.\n\n'
            'Requiere `is_admin=True` y `role=Com`.'
        ),
        request=None,
        responses={
            200: inline_serializer(
                name='RFQTrimmingDeleteResponse',
                fields={'message': drf_serializers.CharField()},
            ),
            400: inline_serializer(
                name='RFQTrimmingDeleteBadRequest',
                fields={'error': drf_serializers.CharField()},
            ),
            404: inline_serializer(
                name='RFQTrimmingDeleteNotFound',
                fields={'detail': drf_serializers.CharField()},
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        rfq = self.get_object()
 
        if rfq.logical_delete:
            return Response(
                {'error': 'Este registro ya fue eliminado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        rfq.logical_delete = True
        rfq.save()

        registrar_historial(
            rfq_tipo = RFQHistorial.Tipo.TRIMMING,
            rfq_id   = rfq.id,
            evento   = RFQHistorial.Evento.CANCELACION,
            actor    = request.user,
        )

        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_cancelacion_confirmada.delay(rfq.id, 'trimming', request.user.id)
        
        return Response(
            {'message': 'Registro eliminado correctamente.'},
            status=status.HTTP_200_OK
        )


