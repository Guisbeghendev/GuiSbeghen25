# quem_sou/views.py
from django.shortcuts import render

def quem_sou(request):
    return render(request, 'quem_sou/quem_sou.html')
