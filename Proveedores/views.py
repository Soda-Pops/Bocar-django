from rest_framework import generics
from .models import Proveedor
from .serializers import ProveedorListSerializer
from users.permissions import IsComercializacionUser


class ProveedorListView(generics.ListAPIView):
    """
    GET /proveedores/
    Devuelve la lista de todos los proveedores registrados.
    Campos: id, company_name, contact_email, account_email,
            country, country_name, continent, continent_name, rating.
    Requiere: role=Com.
    No permite crear, editar ni eliminar proveedores por este medio.
    """
    serializer_class   = ProveedorListSerializer
    permission_classes = [IsComercializacionUser]

    def get_queryset(self):
        return Proveedor.objects.all()