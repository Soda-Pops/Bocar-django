from django.contrib import admin

from .models import RFQHistorial


@admin.register(RFQHistorial)
class RFQHistorialAdmin(admin.ModelAdmin):
    list_display  = ('id', 'rfq_tipo', 'rfq_id', 'evento', 'actor', 'timestamp')
    list_filter   = ('rfq_tipo', 'evento')
    search_fields = ('rfq_id',)
    readonly_fields = (
        'rfq_tipo', 'rfq_id', 'evento', 'actor', 'timestamp',
        'status_anterior', 'status_nuevo', 'cambios', 'detalle',
    )
