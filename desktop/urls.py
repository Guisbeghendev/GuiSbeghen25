# gsdjango/desktop/urls.py

from django.urls import path
from . import views

app_name = 'desktop'

urlpatterns = [
    path('desktop/', views.desktop, name='desktop'),  # Página inicial do painel
    path('create-folder/', views.create_folder, name='create_folder'),  # Criar pasta
    path('upload/', views.upload_files, name='upload_files'),  # Upload de arquivos
]
