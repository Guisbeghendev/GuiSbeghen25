# autenticad/models.py

import os
from django.db import models
from django.contrib.auth.models import User  # Usar o modelo de User nativo do Django
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group  # Importar o modelo Group do Django


class Watermark(models.Model):
    image = models.ImageField(upload_to='watermarks/')  # Imagem da marca d'água
    name = models.CharField(max_length=255, blank=True, null=True)  # Nome da marca d'água
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    thumbnail = models.ImageField(upload_to='watermarks/thumbnails/', blank=True, null=True)  # Miniatura

    def save(self, *args, **kwargs):
        # Verifica se a imagem principal foi fornecida
        if self.image:
            # Abre a imagem
            img = Image.open(self.image)
            img.thumbnail((100, 100))  # Define o tamanho da miniatura

            # Caminho absoluto para salvar a miniatura
            thumb_dir = os.path.join(settings.MEDIA_ROOT, 'watermarks', 'thumbnails')
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)  # Garante que a pasta existe

            thumb_path = os.path.join(thumb_dir, os.path.basename(self.image.name))

            # Salva a miniatura no local gerado
            img.save(thumb_path)

            # Atualiza o campo `thumbnail` com o caminho relativo à pasta `media/`
            self.thumbnail = os.path.relpath(thumb_path, start=settings.MEDIA_ROOT)

        # Salva a instância normalmente
        super(Watermark, self).save(*args, **kwargs)

    def __str__(self):
        return f"Watermark - {self.name if self.name else self.id}"

# Modelo de Diretório (Pasta)
class Directory(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    # Campo para marcar se o diretório foi registrado
    is_registered = models.BooleanField(default=False)  # Marca se o diretório foi registrado no banco
    # Campo para indicar se o diretório já foi usado em uma galeria finalizada
    has_finalized_gallery = models.BooleanField(default=False)  # Marca se o diretório já foi usado em uma galeria

    def __str__(self):
        return self.name


# Galerias
class Gallery(models.Model):
    name = models.CharField(max_length=255)  # Nome da galeria
    event_date = models.DateField()  # Data do evento
    publication_date = models.DateField(auto_now_add=True)  # Data de publicação
    description = models.TextField(blank=True)  # Descrição da galeria
    directory = models.ForeignKey(
        Directory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )  # Diretório relacionado
    watermark = models.ForeignKey(
        Watermark,  # Relacionamento com a marca d'água
        on_delete=models.SET_NULL,  # Permite que a marca d'água seja removida sem excluir a galeria
        null=True,  # Marca d'água é opcional
        blank=True  # Campo pode ser deixado em branco
    )
    is_finalized = models.BooleanField(default=False)  # Marca se a galeria foi finalizada
    group = models.ForeignKey(
        Group,  # Relaciona a galeria a um grupo
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Grupo de usuários que poderão visualizar esta galeria."
    )

    def __str__(self):
        return self.name

    def associate_media(self):
        # Associa as imagens do diretório à galeria
        if self.directory:
            media_files = Media.objects.filter(directory=self.directory)
            for media in media_files:
                media.gallery = self
                media.save()

    def finalize_gallery(self):
        # Finaliza a galeria
        self.is_finalized = True
        self.save()

        # Marca o diretório como utilizado em uma galeria finalizada
        if self.directory:
            self.directory.has_finalized_gallery = True
            self.directory.save()




# Modelo de Imagem/Vídeo com relação ao Diretório
class Media(models.Model):
    file_path = models.ImageField(upload_to='media_files/', max_length=255)  # Caminho do arquivo de mídia
    folder_name = models.CharField(max_length=255, blank=True, null=True)  # Nome da pasta onde o arquivo está
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, related_name="media_files", null=True)  # Alterado para permitir null=True
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="media_files", null=True, blank=True)  # Relacionamento com a galeria
    upload_date = models.DateTimeField(auto_now_add=True)  # Data de upload do arquivo

    def __str__(self):
        return f"Media - {self.id} ({self.folder_name})"


# Modelo de perfil para armazenar informações adicionais
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True)
    how_did_you_know = models.CharField(max_length=255, blank=True)

    # Redes sociais populares
    facebook = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Facebook")
    instagram = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Instagram")
    twitter = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Twitter")
    linkedin = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no LinkedIn")
    tiktok = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no TikTok")
    youtube = models.URLField(max_length=255, blank=True, null=True, help_text="URL do canal no YouTube")
    github = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no GitHub")
    pinterest = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Pinterest")

    # Redes sociais para imagens e criatividade
    flickr = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Flickr")
    deviantart = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no DeviantArt")
    fivehundredpx = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no 500px")
    unsplash = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Unsplash")
    behance = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Behance")
    dribbble = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Dribbble")
    vimeo = models.URLField(max_length=255, blank=True, null=True, help_text="URL do perfil no Vimeo")

    def __str__(self):
        return f"Perfil de {self.user.username}"

