from django.contrib import admin

from .models import Cost_Breakdown_Trimming, Cost_Breakdown_Trimming_File


@admin.register(Cost_Breakdown_Trimming)
class CostBreakdownTrimmingAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_asignacion', 'status', 'last_change', 'last_edited_by')
    list_filter = ('status', 'base_currency_exchange_rate')
    search_fields = ('id_asignacion__id_Proveedor__company_name',)


@admin.register(Cost_Breakdown_Trimming_File)
class CostBreakdownTrimmingFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_cost_breakdown', 'archivo', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
