from django.urls import path
from .views import RFQHistorialView

urlpatterns = [
    # GET — historial completo de una RFQ (mold | trimming)
    path('<str:tipo>/<int:rfq_id>/', RFQHistorialView.as_view(), name='rfq-historial'),
]
