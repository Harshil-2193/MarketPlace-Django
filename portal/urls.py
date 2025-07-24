from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.portal, name='portal'),
    path('login/', views.login_view, name='login_page'),
    path('register/',views.register_view, name="register_page"),
    path('logout/',views.logout_view, name="logout_page"),

]
