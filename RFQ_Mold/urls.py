from django.urls import path
from .views import RFQMoldListCreateView, RFQMoldDetailView

urlpatterns = [
    # URL para guardar y listar todos
    path('rfq-molds/', RFQMoldListCreateView.as_view(), name='rfq-list-create'),
    
    # URL para ver la información de uno en específico (usa la llave primaria 'pk')
    path('rfq-molds/<int:pk>/', RFQMoldDetailView.as_view(), name='rfq-detail'),
]