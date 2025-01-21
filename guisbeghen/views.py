# views.py (diretório principal)

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache  # Ou use banco de dados, se preferir

# View para renderizar a página de política de privacidade
def privacy_policy_view(request):
    return render(request, 'autenticad/privacy_policy.html')


# contador acesso
@csrf_exempt
def visit_counter(request):
    # Recupera o contador de visitas armazenado no cache (ou crie um padrão de 0)
    visits = cache.get('visit_count', 0)
    
    if request.method == 'POST':
        # Incrementa o contador de visitas
        visits += 1
        cache.set('visit_count', visits, timeout=None)  # Armazena novamente no cache (sem expiração)
    
    return JsonResponse({'visit_count': visits})
