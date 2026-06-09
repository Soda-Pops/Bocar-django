from django.contrib import admin
from .models import EvaluacionProveedor


@admin.register(EvaluacionProveedor)
class EvaluacionProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'id_proveedor', 'asignacion_tipo', 'asignacion_id',
        'fue_puntual', 'solicito_extension', 'cotizacion_enviada',
        'calidad_cotizacion', 'comunicacion', 'score', 'fecha_evaluacion',
    )
    list_filter  = ('asignacion_tipo', 'fue_puntual', 'solicito_extension', 'cotizacion_enviada')
    readonly_fields = ('fecha_evaluacion', 'score', 'fue_puntual', 'dias_diferencia', 'solicito_extension', 'cotizacion_enviada')
