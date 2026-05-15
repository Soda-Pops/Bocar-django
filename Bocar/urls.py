from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin -----------------------------------------------------------
    path('admin/', admin.site.urls),

    # Auth ------------------------------------------------------------
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Esquema OpenAPI -------------------------------------------------
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Documentación y UI ----------------------------------------------
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
