from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('getexpensesbyid', views.get_expense_details, name='get_expense_details'),
    path('equal', views.equalDistribution, name='equalDistribution'),
    path('unequal', views.unequalDistribution,name='unequal'),
    path('percentage', views.percentageDistribution,name='percentage'),
]