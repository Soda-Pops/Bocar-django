from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView


urlpatterns = [
    # Admin -----------------------------------------------------------
    path('admin/', admin.site.urls),

    # Auth ------------------------------------------------------------
    path('auth/jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),
    path('auth/jwt/logout/', TokenBlacklistView.as_view(), name='jwt-blacklist'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    # RFQ Mold -------------------------------------------------------
    path('api/v1/mold/', include('RFQ_Mold.urls')),

    # RFQ Trimming --------------------------------------------------
    path('api/v1/trimming/', include('RFQ_Trimming.urls')),

    # Esquema OpenAPI -------------------------------------------------
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Documentación y UI ----------------------------------------------
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
