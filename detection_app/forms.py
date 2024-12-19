from django import forms
from .models import UploadedImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['original_image']

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']