
# autenticad/admin.py

from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Profile, Watermark, Directory, Gallery, Media
from django.contrib.auth.admin import UserAdmin


# Admin para o Profile (relacionado ao User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'birth_date', 'city', 'state']
    search_fields = ['user__username', 'first_name', 'last_name', 'city', 'state']
    list_filter = ['city', 'state']

    def save_model(self, request, obj, form, change):
        # Aqui você pode personalizar a lógica de salvar o profile se necessário
        obj.save()

admin.site.register(Profile, ProfileAdmin)


# Registrando o modelo Watermark
class WatermarkAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'created_at', 'thumbnail']
    list_filter = ['created_at']
    search_fields = ['name']

admin.site.register(Watermark, WatermarkAdmin)


# Registrando o modelo Directory
class DirectoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'path', 'is_registered', 'has_finalized_gallery']
    list_filter = ['is_registered', 'has_finalized_gallery']
    search_fields = ['name', 'path']

admin.site.register(Directory, DirectoryAdmin)


# Registrando o modelo Gallery
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_date', 'publication_date', 'is_finalized', 'group']
    list_filter = ['is_finalized', 'group', 'event_date']
    search_fields = ['name', 'description']
    raw_id_fields = ('directory', 'watermark', 'group')  # Para campos com muitas opções

    def save_model(self, request, obj, form, change):
        # Qualquer lógica adicional que precise para salvar uma galeria
        obj.save()

admin.site.register(Gallery, GalleryAdmin)


# Registrando o modelo Media
class MediaAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'folder_name', 'directory', 'gallery', 'upload_date']
    list_filter = ['directory', 'gallery', 'upload_date']
    search_fields = ['folder_name', 'file_path']

admin.site.register(Media, MediaAdmin)


# Personalizando o painel de administração de usuários
class CustomUserAdmin(UserAdmin):
    # Adiciona 'email', 'first_name', 'last_name' na listagem de usuários
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_active']

    # Adiciona as opções para editar o perfil diretamente pelo painel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}), 
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}), 
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email')}), 
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), 
    )
    filter_horizontal = ('groups', 'user_permissions')  # Facilita a seleção de grupos e permissões

# Registrando o modelo de usuário com a configuração personalizada
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Registrando o modelo Group, mas apenas se não estiver registrado
from django.contrib.admin.sites import site
if not site.is_registered(Group):
    class GroupAdmin(admin.ModelAdmin):
        list_display = ['name']
        search_fields = ['name']

    admin.site.register(Group, GroupAdmin)
