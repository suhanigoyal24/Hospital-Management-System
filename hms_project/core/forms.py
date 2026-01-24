# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']