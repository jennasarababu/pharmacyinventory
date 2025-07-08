from django.urls import path
from . import views
from .views import search_inventory

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('purchase/', views.purchase, name='purchase'),
    path('get_inventory/', views.get_inventory, name='inventory'),
    path('sales/', views.sales, name='sales'),
    path('reports/', views.sales_report, name='reports'),
    path('inventory/', views.inventory, name='inventory'),
    path('purchase_report/', views.purchase_report, name='purchase_report'),
    path('new_purchase/', views.new_purchase, name='new_purchase'),
    path('billing/', views.billing_view, name='billing'),
    path('add_purchase/', views.add_purchase, name='add_purchase'),
    path('get_purchases/', views.get_purchases, name='get_purchases'),
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('invoice_create/', views.invoice_create, name='invoice_create'),
    path('invoice_detail/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoice_list/', views.invoice_list, name='invoice_list'),
    path('fetch_supplier/', views.fetch_supplier, name='fetch_supplier'),
    path('product_search/', views.product_search, name='product_search'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('customer_bill/', views.customer_bill, name='customer_bill'),
    path('search-inventory/', views.search_inventory, name='search_inventory'),
    path('finalize-bill/', views.finalize_bill, name='finalize_bill'),
    path('download-bill/', views.download_bill, name='download_bill'),
    path("recommendation/", views.recommendation_page, name="recommendation_page"),
    path("recommend/", views.get_recommendations, name="get_recommendations"),
    
    
    
]







    

    

