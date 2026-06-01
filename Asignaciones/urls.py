from django.urls import path
from .views import (
    AsignacionesProveedorView,
    AsignacionRFQDetalleView,
    AsignacionResponderView,
    SolicitudExtensionCreateView,
    SolicitudExtensionResolverView,
)

urlpatterns = [
    # GET — devuelve las asignaciones mold y trimming del proveedor autenticado
    path('mis-asignaciones/', AsignacionesProveedorView.as_view(), name='mis-asignaciones'),

    # GET — devuelve el RFQ completo de una asignación específica del proveedor
    # Query param requerido: ?tipo=mold|trimming
    path('detalle/<int:id_asignacion>/', AsignacionRFQDetalleView.as_view(), name='asignacion-rfq-detalle'),

    # POST — el proveedor envía su cost breakdown (una sola vez por asignación)
    # Query param requerido: ?tipo=mold|trimming
    path('responder/<int:id_asignacion>/', AsignacionResponderView.as_view(), name='asignacion-responder'),

    # POST — el proveedor solicita extensión de tiempo para una asignación vencida
    # Query param requerido: ?tipo=mold|trimming
    path('extension/solicitar/<int:id_asignacion>/', SolicitudExtensionCreateView.as_view(), name='extension-solicitar'),

    # PATCH — comercialización aprueba o rechaza una solicitud de extensión
    # Query param requerido: ?tipo=mold|trimming
    path('extension/resolver/<int:id_solicitud>/', SolicitudExtensionResolverView.as_view(), name='extension-resolver'),
]