from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings

from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming

from users.permissions import IsAdminUser
from historial.models import RFQHistorial
from historial.services import registrar_historial
from notificaciones import tasks as notif_tasks

import calendar

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class RFQGlobalCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Dashboard'],
        summary='Conteo global de RFQs',
        description=(
            'Devuelve los contadores globales de RFQs para el dashboard principal:\n\n'
            '- **completados**: RFQs con `complete=True` (mold + trimming).\n'
            '- **en_comercializacion**: RFQs con `status=En_Com`.\n'
            '- **borradores**: RFQs con `status=En_Ind` del usuario indicado '
            '(por defecto el usuario autenticado).\n'
            '- **histograma**: total de RFQs creados por mes del año en curso.\n\n'
            'Solo incluye registros con `logical_delete=False`.'
        ),
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    'ID del usuario cuyos borradores (En_Ind) se contarán. '
                    'Si se omite, se usa el usuario autenticado.'
                ),
            ),
        ],
        responses={
            200: inline_serializer(
                name='RFQGlobalCountResponse',
                fields={
                    'completados': inline_serializer(
                        name='CompletadosCount',
                        fields={
                            'molds':     drf_serializers.IntegerField(),
                            'trimmings': drf_serializers.IntegerField(),
                            'total':     drf_serializers.IntegerField(),
                        },
                    ),
                    'en_comercializacion': inline_serializer(
                        name='EnComCount',
                        fields={
                            'molds':     drf_serializers.IntegerField(),
                            'trimmings': drf_serializers.IntegerField(),
                            'total':     drf_serializers.IntegerField(),
                        },
                    ),
                    'borradores': inline_serializer(
                        name='BorradoresCount',
                        fields={
                            'user_id':   drf_serializers.IntegerField(),
                            'molds':     drf_serializers.IntegerField(),
                            'trimmings': drf_serializers.IntegerField(),
                            'total':     drf_serializers.IntegerField(),
                        },
                    ),
                    'histograma': inline_serializer(
                        name='HistogramaCount',
                        fields={
                            'January':   drf_serializers.IntegerField(),
                            'February':  drf_serializers.IntegerField(),
                            'March':     drf_serializers.IntegerField(),
                            'April':     drf_serializers.IntegerField(),
                            'May':       drf_serializers.IntegerField(),
                            'June':      drf_serializers.IntegerField(),
                            'July':      drf_serializers.IntegerField(),
                            'August':    drf_serializers.IntegerField(),
                            'September': drf_serializers.IntegerField(),
                            'October':   drf_serializers.IntegerField(),
                            'November':  drf_serializers.IntegerField(),
                            'December':  drf_serializers.IntegerField(),
                        },
                    ),
                },
            ),
        },
    )
    def get(self, request):

        # ─── Parámetro opcional: filtrar En_Ind por usuario ───────────────────
        # Si no mandan user_id, usamos el usuario autenticado por defecto
        user_id = request.query_params.get('user_id', request.user.id)

        # ─── Base: solo registros NO borrados lógicamente ─────────────────────
        molds     = RFQ_Mold.objects.filter(logical_delete=False)
        trimmings = RFQ_Trimming.objects.filter(logical_delete=False)

        # ─── 1. Completados ───────────────────────────────────────────────────
        # Suma de RFQ Molds + RFQ Trimmings que tienen complete=True
        molds_completos     = molds.filter(complete=True).count()
        trimmings_completos = trimmings.filter(complete=True).count()
        total_completos     = molds_completos + trimmings_completos

        # ─── 2. En Comercialización ───────────────────────────────────────────
        # Suma de todos los RFQs con status=En_Com sin importar usuario
        molds_en_com     = molds.filter(status=RFQ_Mold.Status.COMERCIALIZACION).count()
        trimmings_en_com = trimmings.filter(status=RFQ_Trimming.Status.COMERCIALIZACION).count()
        total_en_com     = molds_en_com + trimmings_en_com

        # ─── 3. En Industrialización del usuario ─────────────────────────────
        # Solo los RFQs en En_Ind que pertenezcan al user_id recibido
        molds_en_ind     = molds.filter(status=RFQ_Mold.Status.INDUSTRIALIZACION, created_by=user_id).count()
        trimmings_en_ind = trimmings.filter(status=RFQ_Trimming.Status.INDUSTRIALIZACION, created_by=user_id).count()
        total_en_ind     = molds_en_ind + trimmings_en_ind

        # ─── 4. Creacion de Histograma por meses ──────────────────────────────
        meses = calendar.month_name
        hist = {}

        for num_mes, mes in enumerate(meses):
            if num_mes == 0: continue
            molds_en_mes = molds.filter(created_date__month=num_mes).count()
            trimmings_en_mes = trimmings.filter(created_date__month=num_mes).count()
            total_en_mes = molds_en_mes + trimmings_en_mes
            hist[mes] = total_en_mes



        return Response({
            # Completados (ambos tipos, cualquier usuario)
            'completados': {
                'molds':     molds_completos,
                'trimmings': trimmings_completos,
                'total':     total_completos,
            },
            # En Comercialización (ambos tipos, cualquier usuario)
            'en_comercializacion': {
                'molds':     molds_en_com,
                'trimmings': trimmings_en_com,
                'total':     total_en_com,
            },
            # En Industrialización filtrado por usuario
            'borradores': {
                'user_id':   user_id,
                'molds':     molds_en_ind,
                'trimmings': trimmings_en_ind,
                'total':     total_en_ind,
            },
            'histograma': hist
        })


_TIPO_MAP = {
    'mold':     (RFQ_Mold,     RFQHistorial.Tipo.MOLD),
    'trimming': (RFQ_Trimming, RFQHistorial.Tipo.TRIMMING),
}


class RFQLogicalDeleteView(APIView):
    """
    PATCH /api_general/v1/rfq/<id>/delete/?tipo=mold|trimming
    Borrado lógico unificado. Requiere Com Admin.
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in _TIPO_MAP:
            return Response(
                {'error': 'El parámetro "tipo" es requerido y debe ser "mold" o "trimming".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        modelo, historial_tipo = _TIPO_MAP[tipo]
        rfq = get_object_or_404(modelo, pk=pk)

        if rfq.logical_delete:
            return Response(
                {'error': 'Este registro ya fue eliminado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rfq.logical_delete = True
        rfq.save()

        registrar_historial(
            rfq_tipo=historial_tipo,
            rfq_id=rfq.id,
            evento=RFQHistorial.Evento.CANCELACION,
            actor=request.user,
        )

        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_cancelacion_confirmada.delay(rfq.id, tipo, request.user.id)

        return Response(
            {'message': 'Registro eliminado correctamente.'},
            status=status.HTTP_200_OK,
        )


class RFQBorradorDeleteView(APIView):
    """
    DELETE /api_general/v1/rfq/<id>/borrador/?tipo=mold|trimming
    Eliminación física de un RFQ en borrador (En_Ind).
    Solo puede hacerlo el usuario que lo creó.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tipo = request.query_params.get('tipo', '').lower()
        if tipo not in _TIPO_MAP:
            return Response(
                {'error': 'El parámetro "tipo" es requerido y debe ser "mold" o "trimming".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        modelo, _ = _TIPO_MAP[tipo]
        rfq = get_object_or_404(modelo, pk=pk)

        if rfq.status != modelo.Status.INDUSTRIALIZACION:
            return Response(
                {'error': 'Solo se pueden eliminar RFQs en borrador (En_Ind).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rfq.created_by != request.user:
            return Response(
                {'error': 'No tienes permiso para eliminar este borrador.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        rfq.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)