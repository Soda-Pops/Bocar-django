from django.urls import path
from .views import RFQMoldListCreateView, RFQMoldDetailView, RFQMoldCountView

urlpatterns = [
    # 1. Crear (POST) y Listar campos resumidos (GET)
    path('rfq-molds/', RFQMoldListCreateView.as_view(), name='rfq-list-create'),

    # 2. Conteo con filtros opcionales (GET)
    # IMPORTANTE: debe ir ANTES del detalle por ID
    # De lo contrario Django interpreta 'count' como un pk y da error
    path('rfq-molds/count/', RFQMoldCountView.as_view(), name='rfq-count'),

    # 3. Detalle completo por ID (GET) — DELETE y PUT bloqueados automáticamente
    path('rfq-molds/<int:pk>/', RFQMoldDetailView.as_view(), name='rfq-detail'),
]
