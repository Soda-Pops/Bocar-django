from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Aqui editas qué columnas ves en la tabla principal, donde sale toda la lista de usuarios
    list_display = ('username', 'email', 'role','is_admin')

    # Aqui editas que filtros ves y puedes aplicar en la tabla principal de los usuarios
    list_filter = ('role', 'is_staff')

    # Aqui controla qué campos ves cuando abres un usuario que YA EXISTE para editarlo
    # Todo este proceso es para cambiar el orden de las secciones que ves
    base_fieldsets = list(UserAdmin.fieldsets)

    nueva_seccion = ('Informacion de acceso y redireccion', {
        'fields': ('role', 'is_admin'),
        })

    base_fieldsets.insert(2, nueva_seccion)
    fieldsets = tuple(base_fieldsets)

    # Aqui editas o controlas qué campos ves cuando le das a "Añadir usuario"
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informacion de acceso y redireccion', {
            'fields': ('email', 'role', 'is_admin'),
        }),
    )

# Finalmente, le decimos a Django que registre nuestro modelo con esta nueva configuración
admin.site.register(CustomUser, CustomUserAdmin)