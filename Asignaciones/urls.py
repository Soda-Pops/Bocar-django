from django.urls import path
from .views import (
    AsignacionesProveedorView,
    AsignacionRFQDetalleView,
    AsignacionResponderView,
    AsignacionBorradorDetalleView,
    AsignacionBorradorActualizarView,
    AsignacionEnviarRespuestaView,
    SolicitudExtensionCreateView,
    SolicitudExtensionResolverView,
)

urlpatterns = [
    # GET — listado de asignaciones separado en pendientes / contestadas
    path('mis-asignaciones/', AsignacionesProveedorView.as_view(), name='mis-asignaciones'),

    # GET — detalle completo del RFQ de una asignación (sin info de otros proveedores)
    # Query param requerido: ?tipo=mold|trimming
    path('detalle/<int:id_asignacion>/', AsignacionRFQDetalleView.as_view(), name='asignacion-rfq-detalle'),

    # POST — guarda borrador del cost breakdown (status=draft, no marca is_answered)
    # Query param requerido: ?tipo=mold|trimming
    path('responder/<int:id_asignacion>/', AsignacionResponderView.as_view(), name='asignacion-responder'),

    # GET — ver borrador o respuesta guardada
    # Query param requerido: ?tipo=mold|trimming
    path('responder/<int:id_asignacion>/detalle/', AsignacionBorradorDetalleView.as_view(), name='asignacion-borrador-detalle'),

    # PATCH — actualizar borrador (solo si status=draft)
    # Query param requerido: ?tipo=mold|trimming
    path('responder/<int:id_asignacion>/actualizar/', AsignacionBorradorActualizarView.as_view(), name='asignacion-borrador-actualizar'),

    # POST — enviar respuesta definitiva (draft → submitted, marca is_answered=True)
    # Query param requerido: ?tipo=mold|trimming
    path('responder/<int:id_asignacion>/enviar/', AsignacionEnviarRespuestaView.as_view(), name='asignacion-responder-enviar'),

    # POST — el proveedor solicita extensión de tiempo para una asignación vencida
    # Query param requerido: ?tipo=mold|trimming
    path('extension/solicitar/<int:id_asignacion>/', SolicitudExtensionCreateView.as_view(), name='extension-solicitar'),

    # PATCH — comercialización aprueba o rechaza una solicitud de extensión (legacy)
    # Query param requerido: ?tipo=mold|trimming
    path('extension/resolver/<int:id_solicitud>/', SolicitudExtensionResolverView.as_view(), name='extension-resolver'),
]