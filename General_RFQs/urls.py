from django.urls import path
from .views import RFQGlobalCountView, RFQLogicalDeleteView, RFQBorradorDeleteView

urlpatterns = [
    # Conteo global de RFQ Molds + RFQ Trimmings
    # GET /general/rfq-count/                        → usa el usuario autenticado para En_Ind
    # GET /general/rfq-count/?user_id=5              → usa el user_id proporcionado para En_Ind
    path('rfq-count/', RFQGlobalCountView.as_view(), name='rfq-global-count'),

    # Borrado lógico unificado
    # PATCH /api_general/v1/rfq/<id>/delete/?tipo=mold|trimming
    path('rfq/<int:pk>/delete/', RFQLogicalDeleteView.as_view(), name='rfq-logical-delete'),

    # Eliminación física de borrador propio (En_Ind)
    # DELETE /api_general/v1/rfq/<id>/borrador/?tipo=mold|trimming
    path('rfq/<int:pk>/borrador/', RFQBorradorDeleteView.as_view(), name='rfq-borrador-delete'),
]