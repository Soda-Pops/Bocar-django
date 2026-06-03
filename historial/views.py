from datetime import date

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import RFQHistorial
from .serializers import RFQHistorialSerializer


class HistorialPagination(PageNumberPagination):
    page_size            = 20
    page_size_query_param = 'page_size'
    max_page_size        = 100


class RFQHistorialView(APIView):
    """
    GET /api_historial/v1/<tipo>/<rfq_id>/
    Devuelve el historial de eventos de una RFQ (mold o trimming),
    ordenado del más reciente al más antiguo.

    Filtros opcionales (query params):
      - evento=<EVENTO>   uno o varios (repetir el parámetro) — filtra por tipo de evento.
      - actor=<user_id>   filtra por el usuario que ejecutó el evento.
      - desde=YYYY-MM-DD  eventos desde esa fecha (inclusive).
      - hasta=YYYY-MM-DD  eventos hasta esa fecha (inclusive).

    Paginado: page (1 por defecto) y page_size (20 por defecto, máx. 100).
    La respuesta es {count, next, previous, results}.

    Requiere autenticación.
    """
    permission_classes = [IsAuthenticated]
    pagination_class    = HistorialPagination

    @extend_schema(
        summary="Historial de una RFQ",
        description="Timeline de eventos del ciclo de vida de la RFQ, con filtros opcionales.",
        parameters=[
            OpenApiParameter('evento', OpenApiTypes.STR, OpenApiParameter.QUERY,
                             many=True, enum=RFQHistorial.Evento.values,
                             description='Filtra por tipo de evento (repetible).'),
            OpenApiParameter('actor', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description='ID del usuario que ejecutó el evento.'),
            OpenApiParameter('desde', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Fecha inicial (inclusive), YYYY-MM-DD.'),
            OpenApiParameter('hasta', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                             description='Fecha final (inclusive), YYYY-MM-DD.'),
            OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description='Número de página (1 por defecto).'),
            OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description='Tamaño de página (20 por defecto, máx. 100).'),
        ],
        responses={200: RFQHistorialSerializer(many=True)},
    )
    def get(self, request, tipo, rfq_id):
        tipo = tipo.lower()
        if tipo not in (RFQHistorial.Tipo.MOLD, RFQHistorial.Tipo.TRIMMING):
            return Response(
                {'detail': "El tipo debe ser 'mold' o 'trimming'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        eventos = RFQHistorial.objects.filter(rfq_tipo=tipo, rfq_id=rfq_id)

        # ── Filtro por tipo de evento (uno o varios) ──
        eventos_filtro = request.query_params.getlist('evento')
        if eventos_filtro:
            validos = set(RFQHistorial.Evento.values)
            invalidos = [e for e in eventos_filtro if e not in validos]
            if invalidos:
                return Response(
                    {'detail': f"Evento(s) inválido(s): {', '.join(invalidos)}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            eventos = eventos.filter(evento__in=eventos_filtro)

        # ── Filtro por actor ──
        actor = request.query_params.get('actor')
        if actor:
            if not actor.isdigit():
                return Response(
                    {'detail': "El parámetro 'actor' debe ser un id numérico."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            eventos = eventos.filter(actor_id=int(actor))

        # ── Filtro por rango de fechas (sobre la fecha del timestamp) ──
        desde = request.query_params.get('desde')
        if desde:
            fecha = _parse_fecha(desde)
            if fecha is None:
                return _fecha_invalida('desde')
            eventos = eventos.filter(timestamp__date__gte=fecha)

        hasta = request.query_params.get('hasta')
        if hasta:
            fecha = _parse_fecha(hasta)
            if fecha is None:
                return _fecha_invalida('hasta')
            eventos = eventos.filter(timestamp__date__lte=fecha)

        # Orden estable para la paginación (timestamps iguales → desempata por id)
        eventos = eventos.order_by('-timestamp', '-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(eventos, request, view=self)
        serializer = RFQHistorialSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


def _parse_fecha(valor):
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def _fecha_invalida(nombre):
    return Response(
        {'detail': f"El parámetro '{nombre}' debe tener formato YYYY-MM-DD."},
        status=status.HTTP_400_BAD_REQUEST,
    )
