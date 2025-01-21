# reposith/urls.py

from django.urls import path
from . import views

app_name = 'reposith'

urlpatterns = [
    # Rota para criar uma nova galeria
    path('criar-galeria/', views.create_gallery, name='create_gallery'),

    # Rota após a criação da galeria
    path('gallery_created/<int:gallery_id>/', views.gallery_created, name='gallery_created'),

    # Finalizar uma galeria específica
    path('finalize_gallery/<int:gallery_id>/', views.finalize_gallery, name='finalize_gallery'),

    # Listar todas as galerias
    path('list_galleries/', views.list_galleries, name='list_galleries'),

    # Excluir uma galeria
    path('delete_gallery/<int:gallery_id>/', views.delete_gallery, name='delete_gallery'),

    # Listar diretórios disponíveis
    path('list_directories/', views.list_directories, name='list_directories'),

    # Registrar um novo diretório
    path('register_directory/', views.register_directory, name='register_directory'),

    # Dashboard do fotógrafo
    path('fotografo-dashboard/', views.fotografo_dashboard, name='fotografo_dashboard'),

    # Gerenciar marcas d'água
    path('manage_watermark/', views.manage_watermark, name='manage_watermark'),

    # Visualizar detalhes de uma galeria
    path('view_gallery/<int:gallery_id>/', views.view_gallery, name='view_gallery'),

    # Rota para o álbum do usuário final
    path('meualbum/<int:user_id>/', views.meualbum, name='meualbum'),  # Passando o ID do usuário
    path('album/<int:group_id>/<int:user_id>/', views.album, name='album'),
]
