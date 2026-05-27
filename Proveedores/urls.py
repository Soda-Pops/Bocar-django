from django.urls import path
from .views import ProveedorListView

urlpatterns = [
    # Solo GET — ListAPIView bloquea POST, PUT, PATCH y DELETE automáticamente
    path('proveedores/', ProveedorListView.as_view(), name='proveedor-list'),
]