from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Count
from django.conf import settings

from .models import RFQ_Mold, RFQ_Mold_EditRequest
from .serializers import RFQMoldCreateSerializer, RFQMoldDetailSerializer, RFQMoldListSerializer, MoldEditRequestCreateSerializer, MoldEditRequestListSerializer, MoldEditRequestApproveSerializer

# Permisos definidos en la app 'general'
from users.permissions import IsAdminUser, IsComercializacionAdmin

from notificaciones import tasks as notif_tasks
from notificaciones.services import ROL_INDUSTRIALIZACION, ROL_COMERCIALIZACION



class RFQMoldListCreateView(generics.ListCreateAPIView):
    """
    GET  /rfq-molds/
    Devuelve la lista de RFQ Molds activos (logical_delete=False) con campos resumidos.
    Campos: id, status, created_by, created_by_name, created_date, due_date, complete, logical_delete.
 
    POST /rfq-molds/
    Crea un nuevo RFQ Mold. Acepta archivos opcionales bajo el key 'archivos'.
    El campo created_by se asigna automáticamente con el usuario autenticado.
    Enviar como multipart/form-data si se incluyen archivos.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, JSONParser]
 
    def get_queryset(self):
        return RFQ_Mold.objects.filter(logical_delete=False)
 
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RFQMoldCreateSerializer
        return RFQMoldListSerializer
 
    def perform_create(self, serializer):
        archivos = self.request.FILES.getlist('archivos')
        serializer.save(created_by=self.request.user, archivos=archivos)
 
 
class RFQMoldDetailView(generics.RetrieveAPIView):
    """
    GET /rfq-molds/<id>/
    Devuelve todos los campos del RFQ Mold incluyendo archivos adjuntos y nombre del creador.
    También devuelve registros con logical_delete=True para consulta de historial.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = RFQMoldDetailSerializer
 
    def get_queryset(self):
        return RFQ_Mold.objects.all()
 
 
class RFQMoldLogicalDeleteView(UpdateAPIView):
    """
    PATCH /rfq-molds/<id>/delete/
    Marca el RFQ Mold como eliminado (logical_delete=True).
    El registro NO se borra físicamente de la base de datos.
    Retorna error si el registro ya estaba marcado como eliminado.
    Requiere: is_admin=True y role='Com'.
    """
    permission_classes = [IsComercializacionAdmin]
    queryset           = RFQ_Mold.objects.all()
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
            notif_tasks.notificar_cancelacion_confirmada.delay(rfq.id, 'mold', request.user.id)

        return Response(
            {'message': 'Registro eliminado correctamente.'},
            status=status.HTTP_200_OK
        )


class MoldEditRequestCreateView(generics.CreateAPIView):
    """
    POST /rfq-molds/edit-requests/create/
    Crea una solicitud para regresar el status del RFQ Mold de En_Com a En_Ind.
    Validaciones:
      - El RFQ debe estar en status En_Com.
      - No puede existir ya una solicitud Pendiente para el mismo RFQ.
    El campo requested_by se asigna automáticamente con el usuario autenticado.
    """
    serializer_class   = MoldEditRequestCreateSerializer
    permission_classes = [IsAuthenticated]
 
    def perform_create(self, serializer):
        instance = serializer.save(requested_by=self.request.user)
        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_modificacion_rfq.delay(instance.rfq_mold.id, 'mold', self.request.user.id, [ROL_COMERCIALIZACION])


class MoldEditRequestListView(generics.ListAPIView):
    """
    GET /rfq-molds/edit-requests/
    Devuelve todas las solicitudes de edición con status=Pendiente.
    Campos: id, rfq_mold, rfq_mold_status, requested_by, requested_by_name, requested_at, status, reason.
    Requiere: is_admin=True y role=Com.
    """
    serializer_class   = MoldEditRequestListSerializer
    permission_classes = [IsComercializacionAdmin]
 
    def get_queryset(self):
        return RFQ_Mold_EditRequest.objects.filter(status='Pendiente')
 
 
class MoldEditRequestApproveView(UpdateAPIView):
    """
    PATCH /rfq-molds/edit-requests/<id>/approve/
    Aprueba una solicitud de edición pendiente.
    Al aprobar:
      - La solicitud cambia a status=Aprobada.
      - El RFQ Mold cambia su status a En_Ind.
    Validaciones:
      - La solicitud debe estar en status Pendiente.
      - El RFQ no debe estar en status En_Pro.
    Requiere: is_admin=True y role=Com.
    """
    serializer_class   = MoldEditRequestApproveSerializer
    permission_classes = [IsComercializacionAdmin]
    queryset           = RFQ_Mold_EditRequest.objects.all()
    http_method_names  = ['patch']

    def partial_update(self, request, *args, **kwargs):
        edit_request = self.get_object()
        rfq          = edit_request.rfq_mold
        response     = super().partial_update(request, *args, **kwargs)
        if settings.NOTIFICATIONS_ENABLED:
            notif_tasks.notificar_modificacion_rfq.delay(rfq.id, 'mold', request.user.id, [ROL_INDUSTRIALIZACION])
        return response
