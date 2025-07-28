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
]
