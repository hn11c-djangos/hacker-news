# forms.py
from django import forms
from .validators import validate_username

class CreateAccountForm(forms.Form):
    username = forms.CharField(max_length=15, validators=[validate_username])
    password = forms.CharField(widget=forms.PasswordInput)