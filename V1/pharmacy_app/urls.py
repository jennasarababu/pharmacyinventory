
from . import views
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('purchase/', views.purchase, name='purchase'),
    path('sales/', views.sales, name='sales'),
    path('report/', views.report, name='reports'),
    path('inventory/', views.inventory, name='inventory'),
    path('purchase_report/', views.purchase_report, name='purchase_report'),
    path('billing/', views.billing_view, name='billing'),

]