from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('login/', views.login_view, name='login_page'),
    path('register/',views.register_view, name="register_page"),
    path('logout/',views.logout_view, name="logout_page"),
    
    path('', views.portal, name='portal'),
    path('my_products/', views.my_products_view, name="my_products_page"),
    path('create_product/', views.create_product_view, name="create_product_page"),
    path('product_edit/<int:product_id>/', views.edit_product_view, name="edit_product_page"),
    path('product_delete/<int:product_id>/', views.delete_product_view, name="delete_product_page"),
    path('product_details/<int:product_id>/', views.product_details_view, name="product_details_page"),
    
    
    path('create_brand/', views.create_brand_view, name="create_brand_page"),
    path('all_brands/', views.all_brands_view, name="all_brands_page"), 
    path('my_brands/', views.my_brands_view, name="my_brands_page"), 
    path('brand_edit/<str:brand_name>/', views.edit_brand_view, name="edit_brand_page"),
    path('brand_delete/<str:brand_name>/', views.delete_brand_view, name="delete_brand_page"),
    path('brand_products/<str:brand_name>/', views.brand_products_view, name="brand_products_page"),
    
    path('create_category/', views.create_category_view, name="create_category_page"),
    
    path('view_profile/', views.view_profile_view, name="view_profile_page"),
    path('edit_profile/', views.edit_profile_view, name="edit_profile_page"),

    path('search/',views.search_products_view, name="search_products"),
    path('my_products/search/',views.search_my_products_view, name="search_myproducts"),
]
