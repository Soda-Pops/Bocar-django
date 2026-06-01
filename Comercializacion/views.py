from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from users.permissions import IsComercializacionUser
from RFQ_Mold.models import RFQ_Mold
from RFQ_Trimming.models import RFQ_Trimming
from .serializers import (
    RFQMoldComercializacionSerializer,
    RFQTrimmingComercializacionSerializer,
)

from drf_spectacular.utils import extend_schema, inline_serializer


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
