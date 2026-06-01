from django.urls import path
from .views import RFQListComercializacionView

urlpatterns = [
    # GET — lista todos los RFQ activos (mold + trimming) para Comercialización
    path('rfqs/', RFQListComercializacionView.as_view(), name='comercializacion-rfq-list'),
]
