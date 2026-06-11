from django.urls import path
from .views import ProveedorListView, MiPerfilView

urlpatterns = [
    path('proveedores/', ProveedorListView.as_view(), name='proveedor-list'),
    path('mi-perfil/',   MiPerfilView.as_view(),      name='mi-perfil'),
]
