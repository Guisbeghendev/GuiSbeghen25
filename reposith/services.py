# reposith/services.py
from django.shortcuts import render
from reposith.services import prepare_gallery

def prepare_gallery_view(request):
    # Caminho da pasta no servidor (ajuste conforme necessário)
    folder_path = "/caminho/para/a/pasta/no/servidor"

    try:
        media_files = prepare_gallery(folder_path)
        return render(request, 'reposith/success.html', {'media_files': media_files})
    except ValidationError as e:
        return render(request, 'reposith/error.html', {'error': str(e)})
