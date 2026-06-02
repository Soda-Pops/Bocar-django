from django.urls import path
from .views import (
    RFQListComercializacionView,
    CrearAsignacionesView,
    EditRequestAprobarView,
    EditRequestRechazarView,
    SolicitudesPendientesView,
    ExtensionTiempoResolverView,
)

urlpatterns = [
    # GET — lista todos los RFQ activos (mold + trimming) con progreso de proveedores
    path('rfqs/', RFQListComercializacionView.as_view(), name='comercializacion-rfq-list'),

    # GET — solicitudes pendientes de edición (Industrialización) y extensión (Proveedores)
    path('solicitudes/', SolicitudesPendientesView.as_view(), name='comercializacion-solicitudes'),

    # POST — asigna proveedores a un RFQ, omite duplicados, cambia RFQ a En_Pro
    # Query param requerido: ?tipo=mold|trimming
    path('asignaciones/crear/', CrearAsignacionesView.as_view(), name='comercializacion-asignaciones-crear'),

    # PATCH — aprueba solicitud de edición (RFQ vuelve a En_Ind)
    # Query param requerido: ?tipo=mold|trimming
    path('edit-requests/<int:pk>/aprobar/', EditRequestAprobarView.as_view(), name='comercializacion-edit-request-aprobar'),

    # PATCH — rechaza solicitud de edición (RFQ permanece en En_Com)
    # Query param requerido: ?tipo=mold|trimming
    path('edit-requests/<int:pk>/rechazar/', EditRequestRechazarView.as_view(), name='comercializacion-edit-request-rechazar'),

    # PATCH — resuelve solicitud de extensión de tiempo de un proveedor
    # Query param requerido: ?tipo=mold|trimming
    path('extension/<int:pk>/resolver/', ExtensionTiempoResolverView.as_view(), name='comercializacion-extension-resolver'),
]
