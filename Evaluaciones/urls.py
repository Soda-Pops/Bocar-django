from django.urls import path
from .views import CrearEvaluacionView, EvaluacionesProveedorView

urlpatterns = [
    # POST — Compras evalúa la entrega de un proveedor para una asignación
    # Query param requerido: ?tipo=mold|trimming
    path('crear/', CrearEvaluacionView.as_view(), name='evaluacion-crear'),

    # GET — historial de evaluaciones + resumen estadístico de un proveedor
    path('proveedor/<int:id_proveedor>/', EvaluacionesProveedorView.as_view(), name='evaluacion-proveedor'),
]
