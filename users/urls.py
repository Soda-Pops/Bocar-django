from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, MeView

urlpatterns = [
    # users/urls.py
    path('me/', MeView.as_view(), name='auth-me'),
    path('login/',   LoginView.as_view(),       name='login'),
    path('logout/',  LogoutView.as_view(),       name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
]