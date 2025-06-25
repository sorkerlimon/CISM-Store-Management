from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<str:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<str:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    
    # Product URLs
    path('inventory/', views.product_list, name='product_list'),
    path('inventory/add/', views.product_add, name='product_add'),
    path('inventory/<str:product_id>/', views.product_detail, name='product_detail'),
    path('inventory/<str:product_id>/edit/', views.product_edit, name='product_edit'),
    path('inventory/<str:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_add, name='order_add'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/edit/', views.order_edit, name='order_edit'),
    path('orders/<str:order_id>/delete/', views.order_delete, name='order_delete'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/generate/', views.generate_invoice, name='generate_invoice'),
    path('invoices/generate-for-order/<str:order_id>/', views.generate_invoice_for_order, name='generate_invoice_for_order'),
    path('invoices/<str:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<str:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    
    # Ajax endpoints
    path('ajax/get-customer-info/<str:customer_id>/', views.get_customer_info, name='get_customer_info'),
    path('ajax/get-product-info/<str:product_id>/', views.get_product_info, name='get_product_info'),
    
    # API endpoints
    path('api/create_customer/', views.api_create_customer, name='api_create_customer'),
    path('api/upload_products_excel/', views.upload_products_excel, name='upload_products_excel'),
    path('api/customer/<str:customer_id>/', views.api_customer_details, name='api_customer_details'),
    path('api/customer/<str:customer_id>/orders/', views.api_customer_orders, name='api_customer_orders'),
] 