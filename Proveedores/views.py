from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Proveedor
from .serializers import ProveedorListSerializer, ProveedorPerfilSerializer
from users.permissions import IsComercializacionUser, IsProveedor

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


@extend_schema(
    tags=['Proveedores'],
    summary='Perfil del proveedor autenticado',
    description=(
        'Devuelve los datos de perfil del proveedor que tiene la sesión activa.\n\n'
        'Campos: `company_name`, `continent_name`, `country_name`, `rating`.\n\n'
        'Requiere `role=Pro`.'
    ),
    responses={200: ProveedorPerfilSerializer},
)
class MiPerfilView(APIView):
    """
    GET /api_proveedores/v1/mi-perfil/
    Devuelve el perfil del proveedor autenticado.
    Requiere: role=Pro.
    """
    permission_classes = [IsProveedor]

    def get(self, request):
        proveedor = request.user.proveedor
        serializer = ProveedorPerfilSerializer(proveedor)
        return Response(serializer.data)