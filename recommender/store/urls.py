from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    
    # Product purchase routes
    path('purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('purchases/', views.purchase_history, name='purchase_history'),
    
    # Cart management routes
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/buy/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('cart/buy-all/', views.purchase_all, name='purchase_all'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Feedback route
    path('feedback/<int:product_id>/', views.leave_feedback, name='leave_feedback'),
    
    # Authentication routes
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]