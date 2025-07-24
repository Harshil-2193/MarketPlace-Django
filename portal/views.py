from django.shortcuts import render, HttpResponse, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.db import transaction
import logging
logger = logging.getLogger(__name__)
# Login And Register
def login_view(request):

    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('portal')

    if request.method.upper() == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            try:
                user = form.get_user()
                if user is not None:
                    login(request, user)
                    messages.success(request, "Login Successfull")
                    return redirect('portal')
                else:
                    messages.error(request, "Invalid username or password.")
                    logger.warning("Login failed: get_user() returned None")

            except Exception as e:
                messages.error(request, f"Unexpected Error: {e}")
                logger.exception("Unexpected error during login: %s", e)

        else:
            logger.warning("Login form errors: %s", form.errors)
            messages.error(request, f"{form.errors}")
    else:
        form = LoginForm()
        
    return render(request, 'auth/login.html', {'loginForm' : form})

def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('portal')
    
    if request.method.upper() == "POST":

        userForm = UserRegistrationForm(request.POST)
        profileForm = UserProfileForm(request.POST)

        if userForm.is_valid() and profileForm.is_valid():
            try:
                with transaction.atomic():

                    user = userForm.save()
                    profile = profileForm.save(commit=False)
                    profile.user = user
                    profile.save()

                messages.success(request, "User Registered Successfully.")
                return redirect('login_page')
            except Exception as e:
                messages.error(request, f"Unexpected Error: {e}")
                print("Register userForm Exception: ",e)
        else:
            print("Register userForm Error: ",userForm.errors)
            print("Register ProfileForm Error: ",profileForm.errors)
            messages.error(request, f"{userForm.errors} - {profileForm.errors}")
    else:
        userForm = UserRegistrationForm()
        profileForm = UserProfileForm()

    return render(request, 'auth/register.html', {'userForm': userForm, 'profileForm': profileForm})

def logout_view(request):

    if request.user.is_authenticated:
        try:
            username = request.user.username
            logout(request)
            messages.success(request, "You have been logged out successfully.")
            logger.info(f"User: '{username}' logged out. ")
        except Exception as e:
            logger.exception("Error occurred during logout.")
            messages.error(request, "Something went wrong while logging you out.")
    else:
        messages.info(request,"You are not logged in")
    return redirect('login_page')

# Dashboard
def portal(request):
    return render(request, 'portal/dashboard.html')