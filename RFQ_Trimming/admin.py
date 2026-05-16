from django.contrib import admin 
from .models import RFQ_Trimming


class CustomRFQ_TrimmingAdmin(admin.ModelAdmin):

    list_display = ('id', 'status', 'created_by', 'created_date', 'due_date', 'complete', 'logical_delete')
    # Aqui editas que filtros ves y puedes aplicar en la tabla principal de los usuarios
    list_filter = ('status', 'created_date', 'due_date', 'complete', 'logical_delete', 'created_by')
    # Aqui controla qué campos ves cuando abres un usuario que YA EXISTE para editarlo
    # Todo este proceso es para cambiar el orden de las secciones que ves
    
# Finalmente, le decimos a Django que registre nuestro modelo con esta nueva configuración
admin.site.register(RFQ_Trimming, CustomRFQ_TrimmingAdmin)



