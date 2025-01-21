# contato/urls.py
from django.urls import path
from . import views

app_name = 'contato'


urlpatterns = [
    path('', views.contato, name='contato'),  # Página de contato
]
