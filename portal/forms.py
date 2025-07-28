from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="Enter Strong Password"
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        help_text="Enter the same password again for conformation"
    )
    class Meta:
        model = User
        fields = ['username','email','password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2',"Password do not match")

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, *kwargs)
        
        self.fields['role'].choices = [choice for choice in self.fields['role'].choices if choice[0] != '']
        # This wont work as Django renders it a ChopiceField not ModelChoiceField and choicefield doesnt use empty_lable it uses blank=true
        # self.fields['role'].empty_label  =None
        # self.fields['role'].initial = 'Seller'  

        # self.fields['city'].queryset = City.objects.filter(state='Gujarat')
        # if user.is_superuser:
        #  self.fields['role'].queryset = Role.objects.all()
        # else:
        #     self.fields['role'].queryset = Role.objects.exclude(name='Admin'
    class Meta:
        model = UserProfile
        fields = ['name','role']


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['email', 'password']


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name','description']

