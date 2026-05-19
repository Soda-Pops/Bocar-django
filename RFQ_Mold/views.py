from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Count

from .models import RFQ_Mold
from .serializers import (
    RFQMoldCreateSerializer,
    RFQMoldDetailSerializer,
    RFQMoldListSerializer,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. LISTA + CREAR
#    GET  /rfq-molds/  → lista con campos resumidos
#    POST /rfq-molds/  → crea un registro (con archivos opcionales)
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    # MultiPartParser → necesario para recibir archivos (multipart/form-data)
    # JSONParser      → para peticiones GET o POST sin archivos
    parser_classes = [MultiPartParser, JSONParser]

    def get_queryset(self):
        # Excluimos los registros con borrado lógico de la lista por defecto
        # Si quieres verlos todos quita el filter
        return RFQ_Mold.objects.filter(logical_delete=False)

    def get_serializer_class(self):
        # POST → serializer de creación (acepta archivos y todos los campos)
        # GET  → serializer de lista (solo campos de resumen)
        if self.request.method == 'POST':
            return RFQMoldCreateSerializer
        return RFQMoldListSerializer

    def perform_create(self, serializer):
        # Extraemos los archivos del request antes de guardar
        # getlist devuelve lista vacía si no mandaron archivos
        archivos = self.request.FILES.getlist('archivos')

        # created_by se inyecta aquí con el usuario autenticado
        # archivos se pasa al serializer para que los enlace al registro nuevo
        serializer.save(created_by=self.request.user, archivos=archivos)


# ─────────────────────────────────────────────────────────────────────────────
# 2. DETALLE POR ID
#    GET /rfq-molds/<id>/  → todos los campos + archivos adjuntos
#    RetrieveAPIView bloquea automáticamente PUT, PATCH y DELETE
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RFQMoldDetailSerializer

    def get_queryset(self):
        # En el detalle sí mostramos aunque tenga borrado lógico
        # para que se pueda consultar su estado
        return RFQ_Mold.objects.all()


# ─────────────────────────────────────────────────────────────────────────────
# 3. CONTEO CON FILTROS
#    GET /rfq-molds/count/                        → total general
#    GET /rfq-molds/count/?status=En_Ind          → filtrado por status
#    GET /rfq-molds/count/?complete=true          → filtrado por complete
#    GET /rfq-molds/count/?status=En_Ind&complete=false → múltiples filtros
# ─────────────────────────────────────────────────────────────────────────────
class RFQMoldCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Recibimos filtros opcionales desde query params
        status_filtro   = request.query_params.get('status', None)
        complete_filtro = request.query_params.get('complete', None)

        # Construimos el diccionario de filtros dinámicamente
        # Solo agregamos los que realmente llegaron en la URL
        filtros = {}
        if status_filtro:
            filtros['status'] = status_filtro
        if complete_filtro is not None:
            # Los query params llegan como string, convertimos a bool
            filtros['complete'] = complete_filtro.lower() == 'true'

        # Conteo filtrado + conteo agrupado por status en una sola respuesta
        total_filtrado = RFQ_Mold.objects.filter(**filtros).count()

        # Conteo agrupado por status (útil para dashboards)
        por_status = (
            RFQ_Mold.objects
            .values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )

        return Response({
            'filtros_aplicados': filtros if filtros else 'ninguno',
            'total':             total_filtrado,
            'conteo_por_status': list(por_status),
        })
