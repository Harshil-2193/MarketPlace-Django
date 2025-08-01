from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserCombinedProfileForm(forms.Form):
    
    username = forms.CharField(max_length=150, required=True, label='Username')
    email = forms.EmailField(required=True, label='Email')
    name = forms.CharField(max_length=50, required=True, label='Name')
    role = forms.ChoiceField(choices=UserProfile.userRole, required=True, label='Role')

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)
        profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        if user_instance:
            self.fields['username'].initial = user_instance.username
            self.fields['email'].initial = user_instance.email
        if profile_instance:
            self.fields['name'].initial = profile_instance.name
            self.fields['role'].initial = profile_instance.role
    def save(self,user_instance=None, profile_instance=None):
        if not self.is_valid():
            raise ValueError("Cannot save the form if it's not valid.")
        user_instance.username = self.cleaned_data['username']
        user_instance.email = self.cleaned_data['email']
        user_instance.save()

        profile_instance.name = self.cleaned_data['name']
        profile_instance.role = self.cleaned_data['role']
        profile_instance.save()


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
        super(UserProfileForm, self).__init__(*args, **kwargs)

        
        self.fields['role'].choices = [choice for choice in self.fields['role'].choices if  isinstance(choice, tuple) and choice[0] != '']
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

class ProductForm(forms.ModelForm):
    STATUS_CHOICES = (
        (True, 'Active'),
        (False, 'Not Active'),
    )
    status = forms.TypedChoiceField(choices=STATUS_CHOICES, coerce=lambda x: x == 'True', initial=True, widget=forms.RadioSelect,  label="Product Status")
    class Meta:
        model = Product
        fields = ['product_name', 'desc', 'image', 'quantity','status', 'category', 'brand', 'height_cm', 'width_cm']
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'image': forms.ClearableFileInput(attrs={'multiple': False}),
        }

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        if user_profile and user_profile.role == 'seller':
            self.fields['brand'].queryset = Brand.objects.filter(owner=user_profile)
        else:
            self.fields['brand'].queryset = Brand.objects.none()
        self.fields['category'].queryset = Category.objects.all()

        if kwargs.get('instance'):
            self.fields['brand'].disabled = True
            
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }