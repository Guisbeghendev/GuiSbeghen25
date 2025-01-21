from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

# Formulário personalizado de criação de usuário com email
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))  # Campo email estilizado

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')  # Incluindo email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Adiciona a classe 'form-control' a todos os widgets automaticamente
            field.widget.attrs['class'] = 'form-control'


# Formulário para criação de User (Cadastro)
class EditUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        # Adicionando a classe form-control diretamente aos campos
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


# Formulário para edição do profile
class EditProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Data de Nascimento"
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Cidade"
    )
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Estado"
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="Foto de Perfil"
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label="Biografia"
    )
    how_did_you_know = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Como nos conheceu?"
    )
    facebook = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Facebook"
    )
    instagram = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Instagram"
    )
    twitter = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Twitter"
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="LinkedIn"
    )
    tiktok = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="TikTok"
    )
    youtube = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="YouTube"
    )
    github = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="GitHub"
    )
    pinterest = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Pinterest"
    )
    flickr = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Flickr"
    )
    deviantart = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="DeviantArt"
    )
    fivehundredpx = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="500px"
    )
    unsplash = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Unsplash"
    )
    behance = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Behance"
    )
    dribbble = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Dribbble"
    )
    vimeo = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label="Vimeo"
    )

    class Meta:
        model = Profile  # Agora o Profile está sendo referenciado corretamente
        fields = [
            'birth_date', 'city', 'state', 'profile_picture', 'bio', 
            'how_did_you_know', 'facebook', 'instagram', 'twitter', 
            'linkedin', 'tiktok', 'youtube', 'github', 'pinterest', 
            'flickr', 'deviantart', 'fivehundredpx', 'unsplash', 
            'behance', 'dribbble', 'vimeo'
        ]



# Formulário de login com Bootstrap
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica a classe 'form-control' aos campos de login
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'
