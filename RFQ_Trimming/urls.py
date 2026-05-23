from django.urls import path
from .views import RFQTrimmingListCreateView, RFQTrimmingDetailView, RFQTrimmingLogicalDeleteView, TrimmingEditRequestCreateView, TrimmingEditRequestListView, TrimmingEditRequestApproveView

urlpatterns = [
    # 1. Crear (POST) y Listar campos resumidos (GET)
    path('rfq-trimmings/', RFQTrimmingListCreateView.as_view(), name='rfq-trimming-list-create'),

    # 3. Detalle completo por ID (GET) — DELETE y PUT bloqueados automáticamente
    path('rfq-trimmings/<int:pk>/', RFQTrimmingDetailView.as_view(), name='rfq-trimming-detail'),

    # 4. Borrado lógico — solo is_admin=True
    path('rfq-trimmings/<int:pk>/delete/', RFQTrimmingLogicalDeleteView.as_view(), name='rfq-trimming-logical-delete'),

    # 5. Ver solicitudes pendientes — solo admin Comercialización
    path('rfq-trimmings/edit-requests/', TrimmingEditRequestListView.as_view(), name='rfq-trimming-edit-request-list'),

    # 6. Crear solicitud de edición — cualquier usuario autenticado
    path('rfq-trimmings/edit-requests/create/', TrimmingEditRequestCreateView.as_view(), name='rfq-trimming-edit-request-create'),

    # 7. Aprobar solicitud — solo admin Comercialización
    path('rfq-trimmings/edit-requests/<int:pk>/approve/', TrimmingEditRequestApproveView.as_view(), name='rfq-trimming-edit-request-approve'),
]