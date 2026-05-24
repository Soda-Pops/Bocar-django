from django.urls import path
from .views import RFQMoldListCreateView, RFQMoldDetailView, RFQMoldLogicalDeleteView, MoldEditRequestCreateView, MoldEditRequestListView, MoldEditRequestApproveView

urlpatterns = [
    # 1. Crear (POST) y Listar campos resumidos (GET)
    path('rfq-molds/', RFQMoldListCreateView.as_view(), name='rfq-mold-list-create'),
 
    # 2. Detalle completo por ID (GET)
    path('rfq-molds/<int:pk>/', RFQMoldDetailView.as_view(), name='rfq-mold-detail'),
 
    # 3. Borrado lógico — solo is_admin=True
    path('rfq-molds/<int:pk>/delete/', RFQMoldLogicalDeleteView.as_view(), name='rfq-mold-logical-delete'),
 
    # 4. Ver solicitudes pendientes — solo admin Comercialización
    path('rfq-molds/edit-requests/', MoldEditRequestListView.as_view(), name='rfq-mold-edit-request-list'),
 
    # 5. Crear solicitud de edición — cualquier usuario autenticado
    path('rfq-molds/edit-requests/create/', MoldEditRequestCreateView.as_view(), name='rfq-mold-edit-request-create'),
 
    # 6. Aprobar solicitud — solo admin Comercialización
    path('rfq-molds/edit-requests/<int:pk>/approve/', MoldEditRequestApproveView.as_view(), name='rfq-mold-edit-request-approve'),
]
 