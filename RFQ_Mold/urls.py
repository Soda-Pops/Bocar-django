from django.urls import path
from .views import RFQMoldListCreateView, RFQMoldDetailView, RFQMoldLogicalDeleteView

urlpatterns = [
    # 1. Listar campos resumidos (GET) — el POST fue migrado a Industrializacion
    path('rfq-molds/', RFQMoldListCreateView.as_view(), name='rfq-mold-list'),

    # 2. Detalle completo por ID (GET)
    path('rfq-molds/<int:pk>/', RFQMoldDetailView.as_view(), name='rfq-mold-detail'),

    # 3. Borrado lógico — solo is_admin=True
    path('rfq-molds/<int:pk>/delete/', RFQMoldLogicalDeleteView.as_view(), name='rfq-mold-logical-delete'),
]
 