from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Обязательное поле для email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверка на уникальность email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже занят.")
        return email


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']