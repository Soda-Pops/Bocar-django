from django.urls import path

from .views import panel_reentrenamiento


urlpatterns = [
    path('', panel_reentrenamiento, name='panel-reentrenamiento'),
]