from django.urls import path
from . import views
from .views import ProductListView, ProductDetailView, ProductSubcategoryListView, product_subcategory_view, ShippedOrdersListView, ShippedOrdersByUserListView
from catalog.views import RecentOrdersListView
from .views import create_order, register_customer, update_order_status, AllOrdersListView


urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # List of all products
    path('products/', views.ProductListView.as_view(), name='products'),
    
    # List of recent orders for logged-in users
    #path('recentorders/', views.RecentOrdersView, name='recent-orders'),
    
    # Detail view for a specific product by primary key
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Detail view for a specific customer by primary key
    path('customer/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),

    path('product-subcategories/', ProductSubcategoryListView.as_view(), name='product-subcategories'),

    path('subcategory/<int:subcategory_id>/', views.product_subcategory_view, name='product-subcategory'),

    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('recent-orders/', RecentOrdersListView.as_view(), name='recent-orders'),
    path('shipped-orders/', ShippedOrdersListView.as_view(), name='shipped-orders'),
    path('my-shipped-orders/', ShippedOrdersByUserListView.as_view(), name='my-shipped-orders'),

    path('create-order/', create_order, name='create-order'),
    path('register/', register_customer, name='register-customer'),
    path('order/<int:pk>/update-status/', update_order_status, name='update-order-status'),
    path('all-orders/', AllOrdersListView.as_view(), name='all-orders')
]

