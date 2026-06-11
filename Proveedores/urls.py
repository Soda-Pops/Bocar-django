from django.urls import path
from .views import ProveedorListView, MiPerfilView

urlpatterns = [
    # Solo GET — ListAPIView bloquea POST, PUT, PATCH y DELETE automáticamente
    path('proveedores/', ProveedorListView.as_view(), name='proveedor-list'),
    path('mi-perfil/',   MiPerfilView.as_view(),      name='mi-perfil'),
]