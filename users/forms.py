from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserPreference


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['instrument', 'is_lefty','is_printing_alternate_chord']  # Add other fields as needed
          
