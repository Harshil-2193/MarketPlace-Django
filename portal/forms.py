from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email','password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name','role']


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['email', 'password']