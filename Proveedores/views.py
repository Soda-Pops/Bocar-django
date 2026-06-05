from rest_framework import generics
from .models import Proveedor
from .serializers import ProveedorListSerializer
from users.permissions import IsComercializacionUser

from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=['Proveedores'],
    summary='Listar proveedores',
    description=(
        'Devuelve la lista completa de proveedores registrados en el sistema.\n\n'
        'Campos devueltos: `id`, `company_name`, `contact_email`, `account_email`, '
        '`country` (código ISO), `country_name`, `continent` (código), `continent_name`, `rating`.\n\n'
        'Solo lectura — no permite crear, editar ni eliminar proveedores.\n\n'
        'Requiere `role=Com`.'
    ),
    responses={200: ProveedorListSerializer(many=True)},
)
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