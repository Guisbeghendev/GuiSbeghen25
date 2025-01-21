# autenticad/signals.py

from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User
from .models import Profile

def create_roles():
    roles = [
        ('Fotógrafo', 'Permissão de Fotógrafo'),
        ('Administrador', 'Permissão de Administrador'),
        ('Básico', 'Grupo padrão para novos usuários'),  # Inclui o grupo Básico aqui
    ]
    
    for role_name, role_description in roles:
        # Usamos get_or_create para garantir que o grupo seja criado, mas só uma vez
        group, created = Group.objects.get_or_create(name=role_name)
        if created:
            print(f'Grupo {role_name} criado.')
        else:
            print(f'Grupo {role_name} já existia.')

        # Aqui você pode adicionar permissões específicas para o grupo, se necessário
        # Exemplo de como adicionar permissões ao grupo
        # permission = Permission.objects.get(codename='add_gallery')  # Exemplo de permissão
        # group.permissions.add(permission)
        
# Signal para rodar após a migração
@receiver(post_migrate)
def create_roles_after_migration(sender, **kwargs):
    if sender.name == 'autenticad':  # Verifica se o app é o correto
        create_roles()

# Signal para criar perfil e associar ao grupo Básico
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Cria o perfil automaticamente
        Profile.objects.get_or_create(user=instance)

        # Associa ao grupo "Básico" apenas usuários não-superusuários
        if not instance.is_superuser:
            basic_group, _ = Group.objects.get_or_create(name='Básico')  # Certifica-se de que o grupo exista
            instance.groups.add(basic_group)
            print(f"Usuário {instance.username} associado ao grupo Básico.")

# Signal para salvar perfil quando o usuário for salvo
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# **Novo Signal** para sincronizar os campos `first_name` e `last_name` do User com o Profile
@receiver(post_save, sender=User)
def update_profile_from_user(sender, instance, **kwargs):
    # Sincroniza as alterações de `first_name` e `last_name` no Profile
    instance.profile.first_name = instance.first_name
    instance.profile.last_name = instance.last_name
    instance.profile.save()
