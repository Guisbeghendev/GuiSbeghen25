# autenticad/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import RegisterView, CustomLoginView, dashboard_view, profile_view, edit_user, edit_profile, delete_account
from guisbeghen.views import privacy_policy_view

app_name = 'autenticad'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('editar-perfil/', edit_profile, name='edit_profile'),
    path('editar-usuario/', edit_user, name='edit_user'),
    path('perfil/', profile_view, name='perfil'),
    path('delete-account/', delete_account, name='delete_account'),
    path('politica-de-privacidade/', privacy_policy_view, name='privacy_policy'),
]
