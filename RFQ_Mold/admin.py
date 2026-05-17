from django.contrib import admin 
from .models import RFQ_Mold


class CustomRFQ_MoldAdmin(admin.ModelAdmin):

    list_display = ('id', 'status', 'created_by', 'created_date', 'due_date', 'complete', 'logical_delete')
    # Aqui editas que filtros ves y puedes aplicar en la tabla principal de los usuarios
    list_filter = ('status', 'created_date', 'due_date', 'complete', 'logical_delete', 'created_by')
    
# Finalmente, le decimos a Django que registre nuestro modelo con esta nueva configuración
admin.site.register(RFQ_Mold, CustomRFQ_MoldAdmin)



