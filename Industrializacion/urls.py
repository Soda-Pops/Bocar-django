from django.urls import path
from .views import (
    RFQListIndustrializacionView,
    RFQCrearView,
    RFQEditarView,
    RFQEnviarAComercializacionView,
    RFQSolicitarEdicionView,
)

urlpatterns = [
    # GET — listado unificado (borradores=propios, resto=todos)
    path('rfqs/', RFQListIndustrializacionView.as_view(), name='industrializacion-rfq-list'),

    # POST — crea un RFQ del tipo indicado
    # Query param requerido: ?tipo=mold|trimming
    path('rfq/', RFQCrearView.as_view(), name='industrializacion-rfq-crear'),

    # PATCH — edita un RFQ (solo si status=En_Ind)
    # Query param requerido: ?tipo=mold|trimming
    path('rfq/<int:pk>/', RFQEditarView.as_view(), name='industrializacion-rfq-editar'),

    # POST — envía el RFQ a Comercialización (En_Ind → En_Com)
    # Query param requerido: ?tipo=mold|trimming
    path('rfq/<int:pk>/enviar/', RFQEnviarAComercializacionView.as_view(), name='industrializacion-rfq-enviar'),

    # POST — solicita regresar el RFQ a En_Ind (En_Com → En_Ind)
    # Query param requerido: ?tipo=mold|trimming
    path('edit-requests/', RFQSolicitarEdicionView.as_view(), name='industrializacion-edit-request-crear'),
]
