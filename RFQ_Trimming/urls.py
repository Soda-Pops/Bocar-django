from django.urls import path
from .views import RFQTrimmingListCreateView, RFQTrimmingDetailView, RFQTrimmingLogicalDeleteView

urlpatterns = [
    # 1. Listar campos resumidos (GET) — el POST fue migrado a Industrializacion
    path('rfq-trimmings/', RFQTrimmingListCreateView.as_view(), name='rfq-trimming-list'),

    # 2. Detalle completo por ID (GET)
    path('rfq-trimmings/<int:pk>/', RFQTrimmingDetailView.as_view(), name='rfq-trimming-detail'),

    # 3. Borrado lógico — solo is_admin=True
    path('rfq-trimmings/<int:pk>/delete/', RFQTrimmingLogicalDeleteView.as_view(), name='rfq-trimming-logical-delete'),
]