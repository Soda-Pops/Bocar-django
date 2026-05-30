from django.urls import path
from .views import RFQGlobalCountView

urlpatterns = [
    # Conteo global de RFQ Molds + RFQ Trimmings
    # GET /general/rfq-count/                        → usa el usuario autenticado para En_Ind
    # GET /general/rfq-count/?user_id=5              → usa el user_id proporcionado para En_Ind
    path('rfq-count/', RFQGlobalCountView.as_view(), name='rfq-global-count'),
]