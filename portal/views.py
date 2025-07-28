from django.shortcuts import render, HttpResponse, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.db import transaction
import logging
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from .models import *
logger = logging.getLogger(__name__)
# Login And Register
def login_view(request):

    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('portal')

    if request.method == "POST":
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
                return redirect('login_page')
            except Exception as e:
                messages.error(request, f"Unexpected Error: {e}")
                logger.exception("Unexpected error during login: %s", e)
                return redirect('login_page')
        else:
            logger.warning("Login form errors: %s", form.errors)
            messages.error(request, f"{form.errors}")
            return redirect('login_page')
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
                logger.exception("Register userForm Exception: ",e)
                return redirect('register_page')
        else:
            logger.warning("Register userForm Error: ",userForm.errors)
            logger.warning("Register ProfileForm Error: ",profileForm.errors)
            messages.error(request, f"{userForm.errors} - {profileForm.errors}")
            return redirect('register_page')
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
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return render(request, 'portal/dashboard.html')  

# Brand
@login_required(login_url='login_page')
def create_brand_view(request):
    if request.method == "POST":
        brandForm = BrandForm(request.POST)
        if brandForm.is_valid():
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                logger.info(f"UserProfile found: {user_profile}, Role: {user_profile.role}")
                if user_profile.role != 'seller':
                    messages.error(request, "Only sellers can create brands.")
                    return redirect('create_brand_page')

                brand = brandForm.save(commit=False)
                brand.owner = user_profile
                brand.full_clean()
                brand.save()

                messages.success(request, "Brand created successfully.")
                return redirect('portal')

            except UserProfile.DoesNotExist:
                messages.error(request, "No user profile found for this user.")
                return redirect('create_brand_page')
            except Exception as e:
                logger.exception(f"Error during brand creation: {e}")
                messages.error(request, f"Error creating brand: {e}")
                return redirect('create_brand_page')
        else:
            logger.exception("Something wrong while validating brand creation Form")
            messages.error(request, "Enter data in proper format")
            return redirect('create_brand_page')
    else:
        brandForm = BrandForm()
    return render(request, 'portal/create_brand.html', {'brand':brandForm})

def create_category_view(request):
    return render(request, 'portal/create_category.html')

@login_required(login_url='login_page')
def all_brands_view(request):
    try:
        from portal.models import Brand
        for b in Brand.objects.all():
            print(b.brand_name, b.owner.role)

        brand_list = Brand.objects.all()
        # paginator = Paginator(brand_list,3)
        # page = request.GET.get('page')
        # brands = paginator.get_page(page)
        return render(request, 'portal/all_brands.html', {'brands': brand_list})
    except Exception as e:
        logger.error(f"Error in All_Brands_View: {str(e)}")
        return render(request, 'portal/all_brands.html', {'brands': [], 'error': 'Something went wrong while fetching brands.'})

@login_required(login_url='login_page')
def my_brands_view(request):
    try:
        user_profile = UserProfile.objects.get(user = request.user)
        if user_profile.role != 'seller':
            messages.error(request, "Only sellers can view their brands.")
            return redirect('portal')
        brand = Brand.objects.filter(owner = user_profile)
        if not brand.exists():
            messages.info(request, "You have no brands yet.")
            return redirect('portal')
        return render(request, 'portal/my_brands.html', {'brands': brand})
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')
    except Exception as e:
        logger.exception("Error fetching user's brands: %s", e)
        messages.error(request, "Something went wrong while fetching your brands.")
        return redirect('portal')
