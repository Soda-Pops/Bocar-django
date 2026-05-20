from django.contrib import admin
from django.contrib.auth import get_user_model

from Proveedores.models import Proveedor
import RFQ_Mold


# Register your models here.

class CustomProveedorAdmin(admin.ModelAdmin):

    list_display = ('id_account', 'company_name', 'contact_email', 'country', 'continent', 'rating')
    # Aqui editas que filtros ves y puedes aplicar en la tabla principal de los usuarios
    list_filter = ('continent', 'country', 'rating')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'id_account':
            User = get_user_model()
            kwargs['queryset'] = User.objects.filter(role=User.Roles.PROVEEDOR)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
# Finalmente, le decimos a Django que registre nuestro modelo con esta nueva configuración
admin.site.register(Proveedor, CustomProveedorAdmin)



