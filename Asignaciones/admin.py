from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming

User = get_user_model()


class CustomAsignacion_Proveedor_MoldAdmin(admin.ModelAdmin):

    list_display  = (
        'id', 'id_RFQ_Mold', 'id_Proveedor', 'id_user_comercializacion',
        'fecha_de_asignacion', 'due_date', 'is_answered', 'is_closed', 'logical_delete'
    )
    list_filter   = ('is_answered', 'is_closed', 'logical_delete', 'fecha_de_asignacion', 'due_date')
    search_fields = ('id_Proveedor__company_name', 'id_user_comercializacion__email')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtra el dropdown de id_user_comercializacion
        # para mostrar solo usuarios con role='Com'
        if db_field.name == 'id_user_comercializacion':
            kwargs['queryset'] = User.objects.filter(role='Com')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CustomAsignacion_Proveedor_TrimmingAdmin(admin.ModelAdmin):

    list_display  = (
        'id', 'id_RFQ_Trimming', 'id_Proveedor', 'id_user_comercializacion',
        'fecha_de_asignacion', 'due_date', 'is_answered', 'is_closed', 'logical_delete'
    )
    list_filter   = ('is_answered', 'is_closed', 'logical_delete', 'fecha_de_asignacion', 'due_date')
    search_fields = ('id_Proveedor__company_name', 'id_user_comercializacion__email')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtra el dropdown de id_user_comercializacion
        # para mostrar solo usuarios con role='Com'
        if db_field.name == 'id_user_comercializacion':
            kwargs['queryset'] = User.objects.filter(role='Com')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Asignacion_Proveedor_Mold,     CustomAsignacion_Proveedor_MoldAdmin)
admin.site.register(Asignacion_Proveedor_Trimming, CustomAsignacion_Proveedor_TrimmingAdmin)