from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsProveedor
from .models import Asignacion_Proveedor_Mold, Asignacion_Proveedor_Trimming
from .serializers import AsignacionMoldProveedorSerializer, AsignacionTrimmingProveedorSerializer


class AsignacionesProveedorView(APIView):
    """
    GET /asignaciones/mis-asignaciones/
    Devuelve todas las asignaciones del proveedor autenticado,
    separadas en dos listas: mold y trimming.
    Cada asignación incluye: id, rfq_nombre, fecha_de_asignacion, due_date, is_closed.
    Requiere: role='Pro'.
    """
    permission_classes = [IsProveedor]

    def get(self, request):
        # Obtenemos el proveedor ligado al usuario autenticado
        # El related_name='proveedor' en el OneToOneField de Proveedor nos permite esto
        proveedor = request.user.proveedor

        # Filtramos las asignaciones por el proveedor del usuario autenticado
        # y excluimos las que tienen borrado lógico activo
        asignaciones_mold = Asignacion_Proveedor_Mold.objects.filter(
            id_Proveedor=proveedor,
            logical_delete=False
        )
        asignaciones_trimming = Asignacion_Proveedor_Trimming.objects.filter(
            id_Proveedor=proveedor,
            logical_delete=False
        )

        return Response({
            'mold':     AsignacionMoldProveedorSerializer(asignaciones_mold, many=True).data,
            'trimming': AsignacionTrimmingProveedorSerializer(asignaciones_trimming, many=True).data,
        })