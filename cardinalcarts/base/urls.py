from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/<int:product_id>/', views.view_order, name='view_order'),
    path('login', views.login_view, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('cart', views.cart, name='cart'),
    path('cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('admininventory', views.adminInventory, name='adminInventory'),
    path('admininventory/add/', views.add_product, name='add_product'),
    path('admininventory/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admininventory/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('adminorder', views.adminOrder, name='adminOrder'),
    path('adminorder/delete/', views.delete_order, name='delete_order'),
    path('adminorder/add/', views.add_order, name='add_order'),
    path('adminorder/edit/', views.edit_order, name='edit_order'),
    path('admintransaction', views.adminTransaction, name='adminTransaction'),
    path('admin', views.adminUser, name='adminUser'),
    path('admin/add/', views.add_user, name='add_user'),
    path('admin/delete/', views.delete_user, name='delete_user'),
    path('admin/edit/', views.edit_user, name='edit_user'),
    path('orderhistory', views.orderHistory, name='orderHistory'),
    path('vieworder', views.viewOrder, name='viewOrder'),
    path('userlog/', views.user_log, name='user_action_log'),
    path('orderlog/', views.order_action_log, name='order_action_log'),
    path('productlog/', views.product_action_log, name='product_action_log'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('admin/orders/delete/<int:order_id>/', views.delete_order_by_id, name='delete_order_by_id'),
    path('inventory/visualization/', views.inventory_visualization, name='inventory_visualization'),
    path('inventory/visualization/download/', views.download_inventory_report, name='download_inventory_report'),
    path('transactions/visualization/download/', views.download_transactions_report, name='download_transactions_report'),
    path('admin/user/delete/<int:user_id>/', views.delete_user_by_id, name='delete_user_by_id'),
]