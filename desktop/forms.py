# gsdjango/desktop/forms.py

from django import forms

class UploadFilesForm(forms.Form):
    files = forms.FileField(required=True)
