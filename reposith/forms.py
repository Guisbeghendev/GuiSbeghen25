# reposith/forms.py
from django import forms
from autenticad.models import Gallery, Watermark  


# form para marca dagua
class WatermarkForm(forms.ModelForm):
    class Meta:
        model = Watermark
        fields = ['image', 'name']


# form para galeria
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['name', 'event_date', 'description', 'watermark']  # Adiciona o campo de marca d'água

    watermark = forms.ModelChoiceField(
        queryset=Watermark.objects.all(),  # Consulta todas as marcas d'água
        required=False,  # Marca d'água opcional
        widget=forms.Select,
        empty_label="Escolha uma marca d'água"
    )

