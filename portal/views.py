from urllib import request
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.db import transaction
import logging
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
import time
from django.db import connection,reset_queries
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from .models import *
logger = logging.getLogger(__name__)

def get_userRole(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.role
        except UserProfile.DoesNotExist:
            return None
    return None
    
#Login And Register
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
            messages.error(request, "Please enter valid credentials.")
            return render(request, 'auth/login.html', {'loginForm': form})
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
                return render(request, 'auth/register.html', {
                    'userForm': userForm,
                    'profileForm': profileForm
                })
        else:
            logger.warning("Register userForm Error: ",userForm.errors)
            logger.warning("Register ProfileForm Error: ",profileForm.errors)
            return render(request, 'auth/register.html', {
                'userForm': userForm,
                'profileForm': profileForm
            })
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
    return redirect('portal')

#Dashboard
def portal(request):
    reset_queries()
    # start = time.time()

    try:
        products = Product.objects.select_related('brand','owner').filter(status = "True").order_by('-product_id')
        if not products.exists():
            messages.info(request, "You have no Products yet.")
            return redirect('portal')
        
        # for p in products:
        #     _ = p.brand.brand_name
        #     _ = p.owner.user.email

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(products,6)

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

    
    except Exception as e:
        logger.error(f"Error in Products View: {str(e)}")
        messages.error(request, "Something went wrong while fetching products.")
        return render(request, 'portal/dashboard.html', {'products': [],'title': 'Dashboard', 'heading': 'Products', 'error': 'Something went wrong while fetching products.'})
    
    # end = time.time()
    # print("Time Taken: ", end - start)
    # print ("Queries: ", len(connection.queries))
    # for q in connection.queries:
    #     # print(q['sql']) 
    return render(request, 'portal/dashboard.html', {'products': paginated_products,'title': 'Dashboard', 'heading': 'Products','show_actions':False, 'role':get_userRole(request)})


#Product
@login_required(login_url='login_page')
def create_product_view(request):

    def gen_sku():
        import random
        while True:
            sku = str(random.randint(10**11, (10**12) -1))
            if not Product.objects.filter(sku=sku).exists():
                return sku
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role != 'seller':
            messages.error(request, "Only sellers can create products.")
            return redirect('portal')
        if request.method == "POST":
            form =  ProductForm(request.POST, request.FILES, user_profile=user_profile)
            if form.is_valid():
                product = form.save(commit=False)
                product.owner = user_profile
                product.sku = gen_sku()
                product.full_clean()
                product.save()
                messages.success(request, "Product created successfully.")
                return redirect('portal') # Change My products onece gets created leter on
        else:
            form = ProductForm(user_profile=user_profile) # I is required to pass user_profile to the form to get the brands and category created by the user

        return render(request, 'portal/create_product.html', {'productForm': form, 'edit': False})
    
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')
        # brand = Brand.objects.filter(owner = UserProfile.objects.filter(user = request.user).first()).first()

@login_required(login_url='login_page')
def my_products_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        reset_queries()
        # start = time.time()

        if user_profile.role != 'seller':
            messages.error(request, "Only sellers can view their products.")
            return redirect('portal')
        
        products = Product.objects.select_related('brand','owner__user').filter(owner=user_profile).order_by('-product_id')
        
        page = request.GET.get('page',1)
        paginator = Paginator(products, 6)

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)
        # for p in products:
        #     print(p.brand.brand_name)  # accesses foreign key
        #     print(p.owner.user.email)  # nested foreign key

        if not products.exists():
            messages.info(request, "You have no products yet.")
            return redirect('portal')

        # end = time.time()
        # print("Time Taken My: ", end - start)
        # print ("Queries My: ", len(connection.queries))
        # from django.http import JsonResponse
        # after products query and prints
        # if request.GET.get('debug') == '1':
        #     return JsonResponse({
        #         "products_count": products.count(),
        #         "queries": connection.queries,
        #         "time_taken": end - start
        #     })
        return render(request, 'portal/dashboard.html', {'products': paginated_products,'title': 'My Products_', 'heading': 'My Products','show_actions': True})
    
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')
    except Exception as e:
        logger.exception("Error fetching user's products: %s", e)
        messages.error(request, "Something went wrong while fetching your products.")
        return redirect('portal')

@login_required(login_url='login_page')
def edit_product_view(request,product_id):
    product = get_object_or_404(Product, product_id=product_id, owner__user=request.user)

    if product.owner.user != request.user:
        messages.error(request, "You do not have permission to edit this product.")
        return redirect('my_products_page')
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found.")
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None, instance=product,user_profile=user_profile)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product updated successfully.")
                return redirect('my_products_page')
            except Exception as e:
                logger.exception(f"Error updating product: {e}")
                messages.error(request, f"Error updating product: {e}")
                return redirect('edit_product_page', product_id=product_id)
    else:
        form = ProductForm(instance=product, user_profile=user_profile)
        
    return render(request, 'portal/create_product.html', {'productForm': form, 'edit': True})

@login_required(login_url='login_page')
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id, owner__user=request.user)
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile.role == 'seller' or product.owner != user_profile:
        logger.warning(f"Unauthorized delete attempt by user {request.user} on product {product_id}")
        messages.error(request, "You are not authorized to delete this product.")
        return redirect('my_products_page')
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, "Product deleted successfully.")
            logger.info(f"Product {product_id} deleted by user {request.user}")
            return redirect('my_products_page')
        except Exception as e:
            logger.exception(f"Error deleting product: {e}")
            messages.error(request, f"Error deleting product: {e}")
            return redirect('my_products_page')
    messages.error(request, "Invalid request method.")
    return redirect('my_products_page')

def product_details_view(request, product_id):
    try:
        product = get_object_or_404(Product, product_id=product_id)
        if not product.status:
            messages.error(request, "This product is not available.")
            return redirect('my_products_page')
        return render(request, 'portal/product_details.html', {'product': product, 'title': 'Product Details', 'heading': 'Product Details'})
    except ObjectDoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('portal')
    except Exception as e:
        logger.exception(f"Error fetching product details: {e}")
        messages.error(request, "Something went wrong while fetching product details.")
        return redirect('portal')

#Brand
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
    return render(request, 'portal/create_brand.html', {'brand':brandForm, 'edit': False, 'title': 'Create Brand', 'heading': 'Create Brand'})

def all_brands_view(request):
    try:
        from portal.models import Brand
        for b in Brand.objects.all():
            print(b.brand_name, b.owner.role)

        brands = Brand.objects.all()
        # paginator = Paginator(brands,3)
        # page = request.GET.get('page')
        # brands = paginator.get_page(page)
        return render(request, 'portal/all_brands.html', {'brands': brands, 'title': 'Brands','heading': 'Brands','show_actions': False})
    except Exception as e:
        logger.error(f"Error in All_Brands_View: {str(e)}")
        return render(request, 'portal/all_brands.html', {'brands': [], 'error': 'Something went wrong while fetching brands.'})

@login_required(login_url='login_page')
def my_brands_view(request):
    try:
        user_profile = UserProfile.objects.filter(user = request.user).first()
        if user_profile.role != 'seller':
            messages.error(request, "Only sellers can view their brands.")
            return redirect('portal')
        brands= Brand.objects.filter(owner = user_profile)
        if not brands.exists():
            messages.info(request, "You have no brands yet.")
            return redirect('portal')
        return render(request, 'portal/all_brands.html', {'brands': brands, 'is_my':True, 'title': 'My Brands','heading': 'My Brands', 'show_actions': True})
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')
    except Exception as e:
        logger.exception("Error fetching user's brands: %s", e)
        messages.error(request, "Something went wrong while fetching your brands.")
        return redirect('portal')
    
@login_required(login_url='login_page')
def edit_brand_view(request, brand_name):

    brand = get_object_or_404(Brand, brand_name=brand_name, owner__user=request.user)

    if brand.owner.user != request.user:
        messages.error(request, "You do not have permission to edit this product.")
        return redirect('my_products_page')
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("Profile not found.")
    if request.method == 'POST':
        brandFom = BrandForm(request.POST or None, instance=brand)
        if brandFom.is_valid():
            try:
                brandFom.save()
                messages.success(request, "Brand updated successfully.")
                return redirect('my_brands_page')
            except Exception as e:
                logger.exception(f"Error updating brand: {e}")
                messages.error(request, f"Error updating brand: {e}")
                return redirect('edit_brand_page', brand_name=brand_name)
    else:
        brandFom = BrandForm(instance=brand)
    return render(request, 'portal/create_brand.html', {'brand': brandFom, 'edit': True, 'title': 'Edit Brand', 'heading': 'Edit Brand'})

@login_required(login_url='login_page')
def delete_brand_view(request, brand_name):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('my_brands_page')
    
    brand = get_object_or_404(Brand, brand_name=brand_name, owner__user=request.user)
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'seller' or brand.owner != user_profile:
        logger.warning(f"Unauthorized delete attempt by user {request.user} on brand {brand_name}")
        messages.error(request, "You are not authorized to delete this brand.")
        return redirect('my_brands_page')
    try:
        brand.delete()
        messages.success(request, "Brand deleted successfully.")
        logger.info(f"Brand {brand_name} deleted by user {request.user}")
        return redirect('my_brands_page')
    except Exception as e:
        logger.exception(f"Error deleting brand {brand_name}: {e}")
        messages.error(request, f"Error deleting brand {brand_name}: {e}")
        return redirect('my_brands_page')

def brand_products_view(request, brand_name):
    try:
        brand = get_object_or_404(Brand, brand_name=brand_name)
        products = Product.objects.filter(brand=brand,status=True).select_related('owner__user').order_by('-product_id')
        if not products.exists():
            messages.info(request, "No products found for this brand.")
            return render(request, 'portal/all_brands.html', {'brands': [], 'error': 'No products found for this brand.'})
        return render(request,'portal/dashboard.html', {'products': products, 'title': f'Products of {brand_name}', 'heading': f'Products of {brand_name}', 'show_actions': False})
    except Brand.DoesNotExist:
        messages.error(request, "Brand not found.")
        return render(request,'poral/all_brands.html', {'brands': [], 'error': 'Something went wrong while fetching brand products.'})
    except Exception as e:
        logger.exception(f'Error while fetching the brand products:{e}')
        messages.error(request,"Something went wrong while fetching brand products.")
        return render(request,'poral/all_brands.html', {'brands': [], 'error': 'Something went wrong while fetching brand products.'})

#Category
@login_required(login_url='login_page')
def create_category_view(request):
 
    user_profile = UserProfile.objects.filter(user = request.user).first()

    if not user_profile:
        logger.warning(f"No user profile found for user: {request.user}")
        messages.error(request, "User profile not found.")
        return redirect('portal')
    
    if user_profile.role != 'seller':
        logger.warning(f"Unauthorized access by user {request.user} with role {user_profile.role}")
        messages.error(request, "Only sellers can view their brands.")
        return redirect('portal')

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save()
                messages.success(request, "Category created successfully.")
                logger.info(f"Category created by user {request.user}")
                return redirect('portal')
            except Exception as e:
                logger.exception(f"Exception occurred while saving category by user {request.user}: {e}")
                messages.error(request, f"Error creating category: {e}")
                return redirect('create_category_page')
        else:
            logger.warning(f"Form errors while creating category by user {request.user}: {form.errors}")
            messages.error(request, f"{form.errors}")
            return redirect('create_category_page')
    else:
        form = CategoryForm()
    return render(request, 'portal/create_category.html', {'categoryForm': form})

#Profile
@login_required(login_url='login_page')    
def view_profile_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile:
            messages.error(request, "User profile not found.")
            return redirect('portal')
        return render(request, 'portal/view_profile.html', {'profile': user_profile, 'title': 'View Profile', 'heading': 'View Profile'})
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')
    except Exception as e:
        logger.exception(f"Error fetching user profile: {e}")
        messages.error(request, "Something went wrong while fetching your profile.")
        return redirect('portal')
    
@login_required(login_url='login_page')
def edit_profile_view(request):
    try:
       user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('portal')

    if request.method == 'POST':
        form = UserCombinedProfileForm(request.POST, user_instance=request.user, profile_instance=user_profile)
        if form.is_valid():
            try:
                form.save(request.user, user_profile)
                messages.success(request, "Profile updated successfully.")
                return redirect('view_profile_page')
            except Exception as e:
                logger.exception(f"Error updating profile: {e}")
                messages.error(request, f"Error updating profile: {e}")
                return redirect('edit_profile_page')
    else:
        form = UserCombinedProfileForm(user_instance=request.user, profile_instance=user_profile)

        return render(request, 'portal/update_profile.html', {'form': form, 'title': 'Edit Profile', 'heading': 'Edit Profile'})
    
#Serach
def search_products_view(request):
    try:
        query = request.GET.get('q', '').strip()
        if query:
            logger.info(f"Search Query: {query}")
            products = Product.objects.select_related('brand','owner').filter(
                # product_name__icontais = query,
                # product_name__istartswith=query,
                Q(Q(product_name__icontains=query) | Q(product_name__istartswith=query)|Q(sku__icontains=query)),
                status=True
            ).order_by('-product_id')
        else:
            products = Product.objects.select_related('brand', 'owner').filter(status=True).order_by('-product_id')
        html = render_to_string('portal/_product_list.html',{'products':products})
        return JsonResponse({'html': html})
    except Exception as e:
       logger.exception(f"Error while searching products; {e}")
       messages.error(request, "Something went wrong while searching products.")
       return redirect('portal')
    
def search_my_products_view(request):
    try:
        query = request.GET.get('q','').strip()
        user_profile = UserProfile.objects.filter(user=request.user).first()

        if query:
            products = Product.objects.select_related('brand','owner').filter(
                Q(product_name__icontains=query) | Q(product_name__istartswith=query | Q(sku__icontains=query)),
            ).filter(owner=user_profile)
        else:
            products = Product.objects.select_related('brand','owner').filter(owner=user_profile)

        html = render_to_string('portal/_product_list.html', {'products': products})
        return JsonResponse({'html': html})
    
    except Exception as e:
        logger.exception(f"Error while searching my products: {e}")
        messages.error(request,"Something went wrong while searching your products.")
        return redirect('my_products_page')
