from django.urls import path
from .views import AsignacionesProveedorView

urlpatterns = [
    # GET — devuelve las asignaciones mold y trimming del proveedor autenticado
    path('mis-asignaciones/', AsignacionesProveedorView.as_view(), name='mis-asignaciones'),
]