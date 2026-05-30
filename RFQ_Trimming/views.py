from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Count

from .models import RFQ_Trimming, RFQ_Trimming_EditRequest
from .serializers import RFQTrimmingCreateSerializer, RFQTrimmingDetailSerializer, RFQTrimmingListSerializer, TrimmingEditRequestCreateSerializer, TrimmingEditRequestListSerializer, TrimmingEditRequestApproveSerializer

# Importamos los permisos personalizados definidos en la app
# Si los tienes en otra app ajusta el import: from apps.rfq_mold.permissions import ...
from users.permissions import IsAdminUser, IsComercializacionAdmin

from notificaciones import tasks as notif_tasks
from notificaciones.services import ROL_INDUSTRIALIZACION, ROL_COMERCIALIZACION
from Bocar import settings

class RFQTrimmingListCreateView(generics.ListCreateAPIView):
    """
    GET  /rfq-trimmings/
    Devuelve la lista de RFQ Trimmings activos (logical_delete=False) con campos resumidos.
    Campos: id, status, created_by, created_by_name, created_date, due_date, complete, logical_delete.
 
    POST /rfq-trimmings/
    Crea un nuevo RFQ Trimming. Acepta archivos opcionales bajo el key 'archivos'.
    El campo created_by se asigna automáticamente con el usuario autenticado.
    Enviar como multipart/form-data si se incluyen archivos.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, JSONParser]
 
    def get_queryset(self):
        return RFQ_Trimming.objects.filter(logical_delete=False)
 
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RFQTrimmingCreateSerializer
        return RFQTrimmingListSerializer
 
    def perform_create(self, serializer):
        archivos = self.request.FILES.getlist('archivos')
        serializer.save(created_by=self.request.user, archivos=archivos)
 
 
class RFQTrimmingDetailView(generics.RetrieveAPIView):
    """
    GET /rfq-trimmings/<id>/
    Devuelve todos los campos del RFQ Trimming incluyendo archivos adjuntos y nombre del creador.
    También devuelve registros con logical_delete=True para consulta de historial.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = RFQTrimmingDetailSerializer
 
    def get_queryset(self):
        return RFQ_Trimming.objects.all()
 
 
class RFQTrimmingLogicalDeleteView(UpdateAPIView):
    """
    PATCH /rfq-trimmings/<id>/delete/
    Marca el RFQ Trimming como eliminado (logical_delete=True).
    El registro NO se borra físicamente de la base de datos.
    Retorna error si el registro ya estaba marcado como eliminado.
    Requiere: is_admin=True.
    """
    permission_classes = [IsAdminUser]
    queryset           = RFQ_Trimming.objects.all()
    http_method_names  = ['patch']
 
    def partial_update(self, request, *args, **kwargs):
        rfq = self.get_object()
 
        if rfq.logical_delete:
            return Response(
                {'error': 'Este registro ya fue eliminado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        rfq.logical_delete = True
        rfq.save()

        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_cancelacion_confirmada.delay(rfq.id, 'trimming', request.user.id)
        
        return Response(
            {'message': 'Registro eliminado correctamente.'},
            status=status.HTTP_200_OK
        )


class TrimmingEditRequestCreateView(generics.CreateAPIView):
    """
    POST /rfq-trimmings/edit-requests/create/
    Crea una solicitud para regresar el status del RFQ Trimming de En_Com a En_Ind.
    Validaciones:
      - El RFQ debe estar en status En_Com.
      - No puede existir ya una solicitud Pendiente para el mismo RFQ.
    El campo requested_by se asigna automáticamente con el usuario autenticado.
    """
    serializer_class   = TrimmingEditRequestCreateSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        instance = serializer.save(requested_by=self.request.user)
        notif_tasks.notificar_modificacion_rfq.delay(instance.rfq_trimming.id, 'trimming', self.request.user.id, [ROL_COMERCIALIZACION])


class TrimmingEditRequestListView(generics.ListAPIView):
    """
    GET /rfq-trimmings/edit-requests/
    Devuelve todas las solicitudes de edición con status=Pendiente.
    Campos: id, rfq_trimming, rfq_trimming_status, requested_by, requested_by_name, requested_at, status, reason.
    Requiere: is_admin=True y role=Com.
    """
    serializer_class   = TrimmingEditRequestListSerializer
    permission_classes = [IsComercializacionAdmin]
 
    def get_queryset(self):
        return RFQ_Trimming_EditRequest.objects.filter(status='Pendiente')
 
 
class TrimmingEditRequestApproveView(UpdateAPIView):
    """
    PATCH /rfq-trimmings/edit-requests/<id>/approve/
    Aprueba una solicitud de edición pendiente.
    Al aprobar:
      - La solicitud cambia a status=Aprobada.
      - El RFQ Trimming cambia su status a En_Ind.
    Validaciones:
      - La solicitud debe estar en status Pendiente.
      - El RFQ no debe estar en status En_Pro.
    Requiere: is_admin=True y role=Com.
    """
    serializer_class   = TrimmingEditRequestApproveSerializer
    permission_classes = [IsComercializacionAdmin]
    queryset           = RFQ_Trimming_EditRequest.objects.all()
    http_method_names  = ['patch']

    def partial_update(self, request, *args, **kwargs):
        edit_request = self.get_object()
        rfq          = edit_request.rfq_trimming
        response     = super().partial_update(request, *args, **kwargs)
        notif_tasks.notificar_modificacion_rfq.delay(rfq.id, 'trimming', request.user.id, [ROL_INDUSTRIALIZACION])
        return response

