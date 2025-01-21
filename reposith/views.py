# reposith/views.py

import os
from django.db.models.functions import TruncYear
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from autenticad.models import Directory, Media, Gallery, Watermark, Group
from django.contrib.auth.models import User
from datetime import date, datetime
from .forms import WatermarkForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.dateparse import parse_date
from PIL import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import MediaFilter
from django.db.models import Q
from django.http import Http404


# Função para verificar se o usuário está no grupo Fotógrafo ou se é superusuário
def is_photographer(user):
    return user.groups.filter(name='Fotógrafo').exists() or user.is_superuser


# View para listar diretórios
def list_directories(request):
    base_path = os.path.join(settings.MEDIA_ROOT, 'uploads')

    # Cria a pasta 'uploads' se não existir
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Lista os diretórios disponíveis
    available_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    registered_dirs = Directory.objects.filter(is_registered=True).values_list('name', flat=True)
    used_dirs = Directory.objects.filter(has_finalized_gallery=True).values_list('name', flat=True)
    unavailable_dirs = set(registered_dirs) | set(used_dirs)
    available_dirs = [d for d in available_dirs if d not in unavailable_dirs]

    return render(request, 'select_directory.html', {'directories': available_dirs})


# View para registrar diretórios
def register_directory(request):
    if request.method == 'POST':
        selected_dir_name = request.POST.get('directory_name')
        base_path = os.path.join(settings.MEDIA_ROOT, 'uploads')

        if not selected_dir_name:
            return HttpResponse("Por favor, selecione um diretório válido.")

        directory_path = os.path.join(base_path, selected_dir_name)

        if not os.path.exists(directory_path):
            return HttpResponse(f"O diretório '{selected_dir_name}' não existe no caminho informado!")

        if Directory.objects.filter(path=directory_path).exists():
            return render(request, 'error_register.html')

        # Criação do registro no banco para o diretório
        directory = Directory.objects.create(
            path=directory_path,
            name=selected_dir_name,
            is_registered=True
        )

        # Registra os arquivos de mídia do diretório
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, file)
                    Media.objects.create(
                        file_path=file_path,
                        folder_name=os.path.basename(root),
                        directory=directory
                    )

        return render(request, 'success_register.html', {'directory': directory})

    else:
        return redirect('reposith:list_directories')


# View para criar a galeria após estar tudo registrado no banco
@user_passes_test(is_photographer)
def create_gallery(request):
    if request.method == 'POST':
        directory_id = request.POST.get('directory_id')
        directory = get_object_or_404(Directory, id=directory_id)

        if directory.has_finalized_gallery:
            messages.error(request, "Este diretório já foi utilizado em uma galeria finalizada.")
            return redirect('reposith:list_directories')

        gallery_name = request.POST.get('gallery_name')
        event_date_str = request.POST.get('event_date')
        description = request.POST.get('description')

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de data inválido.")
            return redirect('reposith:create_gallery')

        watermark_id = request.POST.get('watermark_id')
        watermark = Watermark.objects.get(id=watermark_id) if watermark_id else None

        group_id = request.POST.get('group_id')
        group = Group.objects.get(id=group_id) if group_id else None

        # Criando a galeria
        gallery = Gallery.objects.create(
            name=gallery_name,
            event_date=event_date,
            description=description,
            directory=directory,
            watermark=watermark,
            group=group  # Associando o grupo à galeria
        )

        # Associar os arquivos de mídia do diretório à galeria
        media_files = Media.objects.filter(directory=directory)
        if not media_files.exists():
            messages.error(request, "Não há arquivos de mídia associados a este diretório.")
            return redirect('reposith:create_gallery')

        # Aplicando a marca d'água se houver
        if watermark:
            watermark_image = Image.open(watermark.image.path)
            for media in media_files:
                image_path = media.file_path.path
                if os.path.exists(image_path):  # Verifica se o arquivo existe
                    try:
                        # Aqui, garantir que o tipo de arquivo será processado adequadamente
                        apply_watermark(image_path, watermark_image)
                    except Exception as e:
                        messages.error(request, f"Erro ao aplicar marca d'água na imagem {media.id}: {e}")
                        return redirect('reposith:create_gallery')

        # Associando as mídias à galeria
        for media in media_files:
            media.gallery = gallery
            media.save()

        # Atualiza o diretório como registrado
        directory.is_registered = True
        directory.save()

        return redirect('reposith:gallery_created', gallery_id=gallery.id)
    else:
        # Filtrando para não incluir os grupos "fotógrafo" e "administrador"
        groups = Group.objects.exclude(name__in=['fotógrafo', 'administrador'])

        # Filtrar apenas diretórios registrados e ainda não finalizados
        directories = Directory.objects.filter(is_registered=True, has_finalized_gallery=False)
        watermarks = Watermark.objects.all()

        return render(request, 'create_gallery.html', {
            'directories': directories,
            'watermarks': watermarks,
            'groups': groups,  # Passando os grupos filtrados para o template
        })




# View para mostrar a galeria criada
def gallery_created(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    return render(request, 'gallery_created.html', {'gallery': gallery})


# View para finalizar a galeria no processo final
def finalize_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)

    if gallery.is_finalized:
        messages.error(request, "Esta galeria já foi finalizada.")
        return redirect('reposith:list_galleries')

    # Verifica se todos os arquivos foram associados corretamente
    media_files = Media.objects.filter(gallery=gallery)
    if not media_files.exists():
        messages.error(request, "Não é possível finalizar a galeria sem arquivos associados.")
        return redirect('reposith:gallery_created', gallery_id=gallery.id)

    if request.method == 'POST':
        gallery.is_finalized = True
        gallery.save()

        if gallery.directory:
            gallery.directory.has_finalized_gallery = True
            gallery.directory.save()

        return redirect('reposith:list_galleries')

    return render(request, 'endgallery.html', {'gallery': gallery})


# Dashboard do Fotógrafo
@user_passes_test(is_photographer)
def fotografo_dashboard(request):
    directories = Directory.objects.all()
    if directories.exists():
        diretoria_registrada = True
    else:
        diretoria_registrada = False

    return render(request, 'fotografo.html', {'diretoria_registrada': diretoria_registrada})


# View para gerenciar a marca d'água
def manage_watermark(request):
    from reposith.forms import WatermarkForm
    if request.method == 'POST':
        form = WatermarkForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('reposith:manage_watermark')
    else:
        form = WatermarkForm()

    watermarks = Watermark.objects.all()

    return render(request, 'manage_watermark.html', {'form': form, 'watermarks': watermarks})


# View para listar as galerias criadas
def list_galleries(request):
    galleries = Gallery.objects.all()

    # Obtém o filtro do ano da URL (se fornecido)
    year_filter = request.GET.get('year')
    
    # Se o filtro de ano for passado e não for vazio
    if year_filter:
        try:
            # Tenta converter o valor para um inteiro
            year_filter = int(year_filter)
            galleries = galleries.filter(event_date__year=year_filter)
        except ValueError:
            # Caso não consiga converter o ano para inteiro, mostrar mensagem de erro
            messages.error(request, 'O valor do ano fornecido é inválido.')

    # Verifica se o filtro por 'finalizada' está ativo
    finalized_filter = request.GET.get('finalized')
    if finalized_filter is not None:
        finalized_filter = finalized_filter.lower() == 'true'  # Transforma em booleano
        galleries = galleries.filter(is_finalized=finalized_filter)

    # Ordena as galerias por data de criação, se necessário
    order = request.GET.get('order', 'asc')
    if order == 'desc':
        galleries = galleries.order_by('-event_date')
    else:
        galleries = galleries.order_by('event_date')

    # Para exibir galeria por ano
    year_choices = Gallery.objects.values('event_date__year').distinct().order_by('event_date__year')
    years = [str(year['event_date__year']) for year in year_choices]  # Lista de anos distintos

    return render(request, 'list_galleries.html', {
        'galleries': galleries,
        'years': years,
        'selected_year': year_filter,
    })


# View para excluir a galeria e seus arquivos
def delete_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)

    if request.method == 'POST':
        media_files = Media.objects.filter(gallery=gallery)
        for media in media_files:
            if media.file_path and os.path.exists(media.file_path.path):
                os.remove(media.file_path.path)
            media.delete()

        gallery.delete()

        messages.success(request, 'Galeria e arquivos excluídos com sucesso.')

        return redirect('reposith:list_galleries')

    return render(request, 'confirm_delete_gallery.html', {'gallery': gallery})


# aplicar marca dagua definitivamente
def apply_watermark(image_path, watermark_image):
    """
    Função para aplicar uma marca d'água sobre uma imagem.
    :param image_path: Caminho para a imagem original
    :param watermark_image: Imagem de marca d'água (PIL Image)
    """
    try:
        original_image = Image.open(image_path)
    except Exception as e:
        print(f"Erro ao abrir a imagem {image_path}: {e}")
        raise

    watermark = watermark_image.convert("RGBA")

    # Log para verificar tamanhos das imagens
    print(f"Imagem Original: {original_image.size}")
    print(f"Marca D'água: {watermark.size}")

    # Obter o tamanho da imagem original e da marca d'água
    original_width, original_height = original_image.size
    watermark_width, watermark_height = watermark.size

    # --- Ajuste de Posição --- 
    # Ajustando a posição da marca d'água para uma margem muito fina das bordas direita e inferior
    margin_fina = 2  # Fina margem em pixels

    position = (
        int(original_width - watermark_width - margin_fina),  # Margem fina na direita
        int(original_height - watermark_height - margin_fina)  # Margem fina embaixo
    )
    # Você pode alterar a posição modificando as coordenadas em `position`.
    # Exemplo:
    # position = (original_width - watermark_width, original_height - watermark_height) # canto inferior direito por padrão
    # position = (0, 0)  # Para colocar no canto superior esquerdo
    # position = (original_width - watermark_width - 10, original_height - watermark_height - 10)  # Para um ajuste com margem
    # position = (original_width // 2 - watermark_width // 2, original_height // 2 - watermark_height // 2)  # Para colocar no centro
    #   position = (
    #   int(original_width - watermark_width - original_width * 0.001),  # Margem de 0,1% na direita
    #   int(original_height - watermark_height - original_height * 0.001)  # Margem de 0,1% embaixo
    #    )

    # --- Ajuste de Tamanho ---
    # Caso queira redimensionar a marca d'água, você pode ajustar o tamanho dela.
    watermark = watermark.resize((int(original_width * 0.1), int(original_height * 0.1)))
    # Exemplo: Redimensionar a marca d'água para ser 10% do tamanho da imagem original
    

    # Colocar a marca d'água sobre a imagem original
    original_image.paste(watermark, position, watermark)  # O último parâmetro é a máscara de alfa

    # Garantir que a imagem de saída será salva no formato correto (mantendo transparência, se houver)
    if original_image.mode != 'RGBA':
        original_image = original_image.convert('RGBA')

    # Salvar a imagem com a marca d'água
    original_image.save(image_path, format='PNG')  # Salvar como PNG para garantir que a transparência seja mantida



def view_gallery(request, gallery_id):
    # Obter a galeria pelo ID
    gallery = get_object_or_404(Gallery, id=gallery_id)
    
    # Obter todas as imagens da galeria (sem filtro, ordenadas por ID)
    media_files = Media.objects.filter(gallery=gallery).order_by('id')

    # Paginação das imagens (24 imagens por página)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(media_files, 24)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # Se o número da página não for um inteiro, pega a primeira página
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # Se a página for vazia, pega a última página
        page_obj = paginator.get_page(paginator.num_pages)

    # Passando o contexto necessário para o template
    return render(request, 'reposith/view_gallery.html', {
        'gallery': gallery,
        'page_obj': page_obj,  # Imagens paginadas (já filtradas e ordenadas)
    })



def meualbum(request, user_id):
    # Garantir que o user_id seja válido e o usuário exista
    user = get_object_or_404(User, pk=user_id)

    # Recuperando os grupos aos quais o usuário pertence
    user_groups = user.groups.all()

    # Se o formulário foi enviado e há um grupo selecionado
    if request.method == 'GET' and 'group_id' in request.GET:
        group_id = request.GET.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        return redirect('reposith:album', group_id=group.id, user_id=user.id)
    
    return render(request, 'reposith/meualbum.html', {
        'user': user,
        'user_groups': user_groups,
        'user_id': user_id,
    })


def album(request, group_id, user_id):
    # Obtendo o usuário logado
    user = get_object_or_404(User, pk=user_id)
    
    # Garantir que o usuário pertence ao grupo
    group = get_object_or_404(Group, id=group_id)
    
    # Verificando se o usuário pertence ao grupo
    if group not in user.groups.all():
        return redirect('reposith:meualbum', user_id=user.id)  # Redireciona caso o usuário não pertença ao grupo
    
    # Filtrando as galerias com base no grupo
    galleries = Gallery.objects.filter(group=group)

    # Filtro por Nome
    name_filter = request.GET.get('name')
    if name_filter:
        galleries = galleries.filter(name__icontains=name_filter)

    # Filtro por Data do Evento
    event_date_filter = request.GET.get('event_date')
    if event_date_filter:
        galleries = galleries.filter(event_date=event_date_filter)

    # Filtro por Ano do Evento
    event_year_filter = request.GET.get('event_year')
    if event_year_filter:
        galleries = galleries.filter(event_date__year=event_year_filter)

    # Filtro por Mês do Evento
    event_month_filter = request.GET.get('event_month')
    if event_month_filter:
        # Converte para inteiro e filtra pelo mês
        event_month_filter = int(event_month_filter)  # Garantir que seja um número inteiro
        galleries = galleries.filter(event_date__month=event_month_filter)

    # Filtro por Data de Publicação
    publication_date_filter = request.GET.get('publication_date')
    if publication_date_filter:
        galleries = galleries.filter(publication_date=publication_date_filter)

    # Definir os meses (de 1 a 12)
    months = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]

    # Agrupando as galerias por nome do grupo (ou outro critério)
    grouped_galleries = {}
    for gallery in galleries:
        group_name = gallery.group.name  # Agrupando pelas galerias de cada grupo
        if group_name not in grouped_galleries:
            grouped_galleries[group_name] = []
        grouped_galleries[group_name].append(gallery)

    # Renderizando a página
    return render(request, 'reposith/album.html', {
        'group': group,
        'galleries': galleries,  # Galerias já filtradas
        'grouped_galleries': grouped_galleries,  # Galerias agrupadas por grupo
        'user': user,  # Passando o usuário para o template
        'months': months  # Passando a lista de meses para o template
    })
