# desktop/views.py

import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

# Função para verificar se o usuário é do grupo Fotógrafo ou superusuário
def is_photographer(user):
    return user.groups.filter(name='Fotógrafo').exists() or user.is_superuser

# View inicial
@user_passes_test(is_photographer)
def desktop(request):
    return render(request, 'desktop/desktop.html')

# View para criar a pasta
@user_passes_test(is_photographer)
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')

        # Definindo o caminho da nova pasta dentro de uploads
        folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            messages.success(request, f'Pasta "{folder_name}" criada com sucesso!')
            return redirect('desktop:upload_files')  # Redireciona para a página de upload
        else:
            messages.error(request, 'Pasta já existe!')

    return render(request, 'desktop/create_folder.html')

# View para enviar arquivos
@user_passes_test(is_photographer)
def upload_files(request):
    # Definindo o caminho base de uploads
    base_upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')

    # Listando pastas vazias
    folder_paths = [
        f for f in os.listdir(base_upload_path)
        if os.path.isdir(os.path.join(base_upload_path, f)) and not os.listdir(os.path.join(base_upload_path, f))
    ]  # Verifica se a pasta está vazia (sem arquivos)

    if request.method == 'POST' and request.FILES.getlist('files'):
        folder_name = request.POST.get('folder_name')
        files = request.FILES.getlist('files')

        # Definindo o caminho da pasta de upload
        upload_dir = os.path.join(base_upload_path, folder_name)

        # Criando o diretório de destino, se necessário
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Salvando os arquivos no diretório da pasta escolhida
        for file in files:
            file_path = os.path.join(upload_dir, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        # Renderizando a página de sucesso
        return render(request, 'desktop/upload_success.html', {'message': 'Arquivos enviados com sucesso!'})

    return render(request, 'desktop/upload.html', {'folders': folder_paths})
