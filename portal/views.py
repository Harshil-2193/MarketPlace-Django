from django.shortcuts import render, HttpResponse, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate


# Login And Register
def login_view(request):
    if request.method.upper() == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_validate():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login Successfull")
            return redirect('portal')
        else:
            print("Login Form Error: ",form.errors)
            messages.error(request, f"{form.errors}")
    else:
        form = LoginForm()
        
    return render(request, 'auth/login.html', {'loginForm' : form})
def register_view(request):
    if request.method.upper() == "POST":

        userForm = UserRegistrationForm(request.POST)
        profileForm = UserProfileForm(request.POST)

        if userForm.is_valid() and profileForm.is_validate():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()

            profile = profileForm.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "User Registered Successfully.")
            return redirect('login_page')
        else:
            print("Register userForm Error: ",userForm.errors)
            print("Register ProfileForm Error: ",profileForm.errors)
            messages.error(request, f"{userForm.errors} - {profileForm.errors}")
    else:
        userForm = UserRegistrationForm()
        profileForm = UserProfileForm()

    return render(request, 'auth/register.html', {'userForm': userForm, 'profileForm': profileForm})

# Dashboard
def portal(request):
    return render(request, 'portal/dashboard.html')