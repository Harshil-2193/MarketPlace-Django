from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.portal, name='portal'),
    path('login/', views.login_view, name='login_page'),
    path('register/',views.register_view, name="register_page"),
    path('logout/',views.logout_view, name="logout_page"),
    path('create_brand/', views.create_brand_view, name="create_brand_page"),
    path('create_category/', views.create_category_view, name="create_category_page"),
    path('all_brands/', views.all_brands_view, name="all_brands_page"), 
    path('my_brands/', views.my_brands_view, name="my_brands_page"), 
    path('create_product/', views.create_product_view, name="create_product_page"),
    path('create_category/', views.create_category_view, name="create_category_page"),
    path('my_products/', views.my_products_view, name="my_products_page"),
    path('product_edit/<int:product_id>/', views.edit_product_view, name="edit_product_page"),
    path('product_delete/<int:product_id>/', views.delete_product_view, name="delete_product_page"),
    # path('product_delete/', views.my_products_view, name="my_products_page"),
]
