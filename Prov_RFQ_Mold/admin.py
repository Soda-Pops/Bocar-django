from django.contrib import admin

from .models import Cost_Breakdown_Mold, Cost_Breakdown_Mold_File, Set_of_Cavities_Mold


@admin.register(Cost_Breakdown_Mold)
class CostBreakdownMoldAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_asignacion', 'status', 'last_change', 'last_edited_by')
    list_filter = ('status', 'base_currency_exchange_rate')
    search_fields = ('id_asignacion__id_Proveedor__company_name',)


@admin.register(Set_of_Cavities_Mold)
class SetOfCavitiesMoldAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_cost_breakdown')


@admin.register(Cost_Breakdown_Mold_File)
class CostBreakdownMoldFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_cost_breakdown', 'archivo', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
