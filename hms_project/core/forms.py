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

    # <-- fixed indentation
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']  # save the role
        if commit:
            user.save()
        return user
