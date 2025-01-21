# autenticad/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, EditProfileForm, EditUserForm, CustomAuthenticationForm
from .models import Profile


# criar novo user
class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm  # Usando o formulário com e-mail
    template_name = 'autenticad/register.html'
    success_url = reverse_lazy('autenticad:login')

    def form_valid(self, form):
        # Cria o usuário e salva a senha
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])  # Garantindo que a senha seja salva corretamente
        user.save()

        # Realiza o login automaticamente após o cadastro
        login(self.request, user)

        return redirect(self.success_url)


# Login com CBV (LoginView)
class CustomLoginView(LoginView):
    template_name = 'autenticad/login.html'
    form_class = CustomAuthenticationForm  # Use o seu formulário personalizado

    def get_success_url(self):
        return reverse_lazy('autenticad:dashboard')

    def form_valid(self, form):
        # Aqui você pode adicionar lógica extra antes de retornar o sucesso, se necessário.
        return super().form_valid(form)

# Dashboard view
@login_required
def dashboard_view(request):
    # Verifica se o usuário está no grupo 'fotografo' ou se é superusuário
    is_fotografo_or_superuser = request.user.groups.filter(name='fotografo').exists() or request.user.is_superuser
    
    # Verifica se o usuário está no grupo 'administrador' ou se é superusuário
    is_administrador_or_superuser = request.user.groups.filter(name='administrador').exists() or request.user.is_superuser

    # Passa as variáveis para o template
    return render(request, 'autenticad/dashboard.html', {
        'is_fotografo_or_superuser': is_fotografo_or_superuser,
        'is_administrador_or_superuser': is_administrador_or_superuser,
        'user': request.user,  # Garantir que o objeto 'user' é passado corretamente para o template
    })


# Perfil do usuário
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile  # Acessa o perfil associado ao usuário
    context = {'user': user, 'profile': profile}
    return render(request, 'autenticad/profile.html', context)

# Editar perfil do usuário
@login_required
def edit_user(request):
    user = request.user
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            return redirect('autenticad:perfil')
    else:
        user_form = EditUserForm(instance=user)

    return render(request, 'autenticad/edit_user.html', {'user_form': user_form})

@login_required
# Editar perfil do usuário
def edit_profile(request):
    try:
        profile = request.user.profile  # Garantir que o perfil do usuário existe
    except Profile.DoesNotExist:
        # Caso o perfil não exista, redireciona para uma página de erro ou criação de perfil
        return redirect('autenticad:create_profile')  # Exemplo de redirecionamento para criação de perfil, caso necessário

    if request.method == 'POST':
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()  # Salva as alterações no perfil
            return redirect('autenticad:perfil')  # Redireciona para a página de perfil após salvar
        else:
            # Caso o formulário não seja válido, retornamos o mesmo template com o formulário e erros
            return render(request, 'autenticad/edit_profile.html', {'profile_form': profile_form})
    else:
        # Quando for uma requisição GET, preenche o formulário com os dados do perfil
        profile_form = EditProfileForm(instance=profile)

    return render(request, 'autenticad/edit_profile.html', {'profile_form': profile_form})



# Deletar conta do usuário
@login_required
def delete_account(request):
    user = request.user
    user.delete()  # Exclui o usuário
    logout(request)  # Faz o logout após excluir a conta
    return redirect('autenticad:login')  # Redireciona para a página de login
