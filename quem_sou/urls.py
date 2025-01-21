# quem_sou/urls.py
from django.urls import path
from . import views

app_name = 'quem_sou'  # Define o namespace para as URLs desta aplicação

urlpatterns = [
    path('', views.quem_sou, name='quem_sou'),  # Definindo a rota para a página Quem Sou
]
