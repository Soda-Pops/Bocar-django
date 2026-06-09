from rest_framework import serializers
from .models import EvaluacionProveedor


class CrearEvaluacionSerializer(serializers.Serializer):
    """Body que recibe Compras al crear una evaluación."""

    asignacion_id      = serializers.IntegerField(min_value=1)
    calidad_cotizacion = serializers.IntegerField(min_value=1, max_value=5)
    comunicacion       = serializers.IntegerField(min_value=1, max_value=5)
    comentarios        = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        # Verificar que no exista ya una evaluación para esta asignación+tipo
        tipo = self.context.get('asignacion_tipo')
        ya_existe = EvaluacionProveedor.objects.filter(
            asignacion_tipo=tipo,
            asignacion_id=attrs['asignacion_id'],
        ).exists()
        if ya_existe:
            raise serializers.ValidationError(
                {'asignacion_id': 'Esta asignación ya tiene una evaluación registrada.'}
            )
        return attrs


class EvaluacionProveedorSerializer(serializers.ModelSerializer):
    """Lectura completa de una evaluación."""

    proveedor_nombre = serializers.CharField(
        source='id_proveedor.company_name', read_only=True
    )
    evaluado_por_email = serializers.EmailField(
        source='evaluado_por.email', read_only=True
    )

    class Meta:
        model  = EvaluacionProveedor
        fields = [
            'id',
            'asignacion_tipo',
            'asignacion_id',
            'proveedor_nombre',
            'evaluado_por_email',
            'fecha_evaluacion',
            'fue_puntual',
            'dias_diferencia',
            'solicito_extension',
            'cotizacion_enviada',
            'calidad_cotizacion',
            'comunicacion',
            'comentarios',
            'score',
        ]


class ResumenProveedorSerializer(serializers.Serializer):
    """Estadísticas agregadas del proveedor para Compras."""

    proveedor_id      = serializers.IntegerField()
    company_name      = serializers.CharField()
    rating_actual     = serializers.FloatField()
    total_evaluaciones = serializers.IntegerField()
    pct_puntual       = serializers.FloatField()
    pct_sin_extension = serializers.FloatField()
    pct_cotizacion_enviada = serializers.FloatField()
    promedio_calidad  = serializers.FloatField()
    promedio_comunicacion = serializers.FloatField()
    evaluaciones      = EvaluacionProveedorSerializer(many=True)
