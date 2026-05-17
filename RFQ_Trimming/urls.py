from django.urls import path
from .views import RFQTrimmingDetailView, RFQTrimmingListCreateView

urlpatterns = [
    # URL para guardar y listar todos
    path('rfq-trimming/', RFQTrimmingListCreateView.as_view(), name='rfq-list-create'),
    
    # URL para ver la información de uno en específico (usa la llave primaria 'pk')
    path('rfq-trimming/<int:pk>/', RFQTrimmingDetailView.as_view(), name='rfq-detail'),
]