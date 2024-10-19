from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('getusers', views.getUsers, name='get-all-user'),
    path('register', views.userRegister, name='user-register'),
    path('login', views.userLogin,name='user-login'),
    path('logout', views.userLogout,name='user-logout'),
]