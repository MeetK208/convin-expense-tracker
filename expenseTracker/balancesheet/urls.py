from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('individual-sheet', views.individualBalanceSheet, name='individualBalanceSheet'),
    path('overall-sheet', views.overallBalanceSheet,name='overallBalanceSheet'),
]