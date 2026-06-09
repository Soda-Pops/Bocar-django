from django.db.models import Avg, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from users.permissions import IsComercializacionUser
from Proveedores.models import Proveedor
from Asignaciones.models import (
    Asignacion_Proveedor_Mold,
    Asignacion_Proveedor_Trimming,
)
from historial.models import RFQHistorial
from historial.services import registrar_historial

from .models import EvaluacionProveedor
from .serializers import (
    CrearEvaluacionSerializer,
    EvaluacionProveedorSerializer,
    ResumenProveedorSerializer,
)
from .services import calcular_metricas, calcular_score, recalcular_rating_proveedor

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


_TIPO_PARAM = OpenApiParameter(
    name='tipo',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    required=True,
    enum=['mold', 'trimming'],
)


class CrearEvaluacionView(APIView):
    """
    POST /api_evaluaciones/v1/crear/?tipo=mold|trimming
    Compras evalúa la entrega de un proveedor para una asignación cerrada.
    Las métricas objetivas se calculan automáticamente; Compras solo ingresa
    calidad_cotizacion (1-5), comunicacion (1-5) y comentarios.
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Crear evaluación de proveedor",
        description="""
            Crea una evaluación para una asignación (mold o trimming).
            Las métricas de puntualidad, extensiones y envío de cotización se calculan
            automáticamente a partir de los datos existentes.
            Compras proporciona la calificación manual (1-5) de calidad y comunicación.
            Solo se puede evaluar una vez por asignación.
            Requiere role='Com'.
        """,
        parameters=[_TIPO_PARAM],
        request=CrearEvaluacionSerializer,
        responses={
            201: inline_serializer(
                name='EvaluacionCreadaResponse',
                fields={
                    'detail': serializers.CharField(),
                    'score':  serializers.FloatField(),
                    'nuevo_rating_proveedor': serializers.FloatField(),
                }
            ),
            400: inline_serializer(
                name='EvaluacionCreadaBadRequest',
                fields={'detail': serializers.CharField()}
            ),
            404: inline_serializer(
                name='EvaluacionCreadaNotFound',
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

        serializer = CrearEvaluacionSerializer(
            data=request.data,
            context={'asignacion_tipo': tipo},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Verificar que la asignación existe
        if tipo == 'mold':
            try:
                asignacion = Asignacion_Proveedor_Mold.objects.select_related(
                    'id_Proveedor'
                ).get(id=data['asignacion_id'])
            except Asignacion_Proveedor_Mold.DoesNotExist:
                return Response(
                    {'detail': 'Asignación Mold no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            try:
                asignacion = Asignacion_Proveedor_Trimming.objects.select_related(
                    'id_Proveedor'
                ).get(id=data['asignacion_id'])
            except Asignacion_Proveedor_Trimming.DoesNotExist:
                return Response(
                    {'detail': 'Asignación Trimming no encontrada.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        proveedor = asignacion.id_Proveedor

        # Calcular métricas automáticas
        metricas = calcular_metricas(tipo, data['asignacion_id'])

        # Calcular score ponderado
        score = calcular_score(
            fue_puntual        = metricas['fue_puntual'],
            dias_diferencia    = metricas['dias_diferencia'],
            solicito_extension = metricas['solicito_extension'],
            cotizacion_enviada = metricas['cotizacion_enviada'],
            calidad_cotizacion = data['calidad_cotizacion'],
            comunicacion       = data['comunicacion'],
        )

        evaluacion = EvaluacionProveedor.objects.create(
            asignacion_tipo    = tipo,
            asignacion_id      = data['asignacion_id'],
            id_proveedor       = proveedor,
            evaluado_por       = request.user,
            fue_puntual        = metricas['fue_puntual'],
            dias_diferencia    = metricas['dias_diferencia'],
            solicito_extension = metricas['solicito_extension'],
            cotizacion_enviada = metricas['cotizacion_enviada'],
            calidad_cotizacion = data['calidad_cotizacion'],
            comunicacion       = data['comunicacion'],
            comentarios        = data.get('comentarios', ''),
            score              = score,
        )

        nuevo_rating = recalcular_rating_proveedor(proveedor)

        # Obtener rfq_id para el historial
        if tipo == 'mold':
            rfq_id = asignacion.id_RFQ_Mold_id
        else:
            rfq_id = asignacion.id_RFQ_Trimming_id

        registrar_historial(
            rfq_tipo = tipo,
            rfq_id   = rfq_id,
            evento   = RFQHistorial.Evento.EVALUACION_PROVEEDOR,
            actor    = request.user,
            detalle  = {
                'proveedor':    proveedor.company_name,
                'score':        score,
                'nuevo_rating': nuevo_rating,
            },
        )

        return Response(
            {
                'detail':                 'Evaluación registrada correctamente.',
                'score':                  score,
                'nuevo_rating_proveedor': nuevo_rating,
            },
            status=status.HTTP_201_CREATED,
        )


class EvaluacionesProveedorView(APIView):
    """
    GET /api_evaluaciones/v1/proveedor/<id_proveedor>/
    Lista todas las evaluaciones de un proveedor con su resumen estadístico.
    Requiere role='Com'.
    """
    permission_classes = [IsComercializacionUser]

    @extend_schema(
        summary="Evaluaciones y resumen de un proveedor",
        description="""
            Devuelve el historial completo de evaluaciones de un proveedor junto con
            estadísticas agregadas: % puntualidad, % sin extensiones, promedios de
            calidad y comunicación, y rating actual.
            Requiere role='Com'.
        """,
        responses={
            200: ResumenProveedorSerializer,
            404: inline_serializer(
                name='EvaluacionesNotFound',
                fields={'detail': serializers.CharField()}
            ),
        },
    )
    def get(self, request, id_proveedor):
        try:
            proveedor = Proveedor.objects.get(id=id_proveedor)
        except Proveedor.DoesNotExist:
            return Response(
                {'detail': 'Proveedor no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        evaluaciones = EvaluacionProveedor.objects.filter(
            id_proveedor=proveedor
        ).select_related('evaluado_por')

        total = evaluaciones.count()

        if total > 0:
            agg = evaluaciones.aggregate(
                puntual_count    = Count('id', filter=Q(fue_puntual=True)),
                sin_ext_count    = Count('id', filter=Q(solicito_extension=False)),
                cotizacion_count = Count('id', filter=Q(cotizacion_enviada=True)),
                avg_calidad      = Avg('calidad_cotizacion'),
                avg_comunicacion = Avg('comunicacion'),
            )
            pct_puntual        = round(agg['puntual_count']    / total * 100, 1)
            pct_sin_extension  = round(agg['sin_ext_count']    / total * 100, 1)
            pct_cotizacion     = round(agg['cotizacion_count'] / total * 100, 1)
            promedio_calidad   = round(agg['avg_calidad'] or 0.0, 2)
            promedio_comunicacion = round(agg['avg_comunicacion'] or 0.0, 2)
        else:
            pct_puntual = pct_sin_extension = pct_cotizacion = 0.0
            promedio_calidad = promedio_comunicacion = 0.0

        resumen = {
            'proveedor_id':           proveedor.id,
            'company_name':           proveedor.company_name,
            'rating_actual':          proveedor.rating,
            'total_evaluaciones':     total,
            'pct_puntual':            pct_puntual,
            'pct_sin_extension':      pct_sin_extension,
            'pct_cotizacion_enviada': pct_cotizacion,
            'promedio_calidad':       promedio_calidad,
            'promedio_comunicacion':  promedio_comunicacion,
            'evaluaciones':           EvaluacionProveedorSerializer(evaluaciones, many=True).data,
        }

        return Response(ResumenProveedorSerializer(resumen).data, status=status.HTTP_200_OK)
