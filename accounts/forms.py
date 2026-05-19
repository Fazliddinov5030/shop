from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'adress',
            'email',
            'birth_date',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control date-input'}),
        }
