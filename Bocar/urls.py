from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    # Admin -----------------------------------------------------------
    path('admin/', admin.site.urls),

    # Auth ------------------------------------------------------------
    path('auth/', include('users.urls')),

    # RFQ Mold --------------------------------------------------------
    path('api_mold/v1/', include('RFQ_Mold.urls')),

    # RFQ Trimming ----------------------------------------------------
    path('api_trimming/v1/', include('RFQ_Trimming.urls')),

    # General endpoints -----------------------------------------------
    path('api_general/v1/', include('General.urls')),

    # Esquema OpenAPI -------------------------------------------------
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Documentación y UI ----------------------------------------------
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
