# gsdjango/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import visit_counter  # Importe a view corretamente
from django.conf import settings  # Importando settings
from django.conf.urls.static import static  # Importando static

urlpatterns = [
    path('admin/', admin.site.urls),  # Rotas do painel de administração
    path('api/visit-counter/', visit_counter, name='visit_counter'),  # Corrigido: referenciando diretamente a view
    path('', include('home.urls')),  # Rotas do app Home
    path('quem-sou/', include('quem_sou.urls')),  # Rotas do app Quem Sou
    path('contato/', include('contato.urls')),  # Rotas do app Contato
    path('auth/', include('autenticad.urls')),  # Rotas do app Autenticad (autenticação)
    path('desktop/', include('desktop.urls')),  # Rota para o app Desktop
    path('reposith/', include('reposith.urls')), # Rota para o app Reposith
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
