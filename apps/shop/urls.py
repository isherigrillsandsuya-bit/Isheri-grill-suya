from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('cart/add/<int:item_id>/', views.add_to_cart_view, name='add_to_cart'),
    
    # New Endpoints
    path('checkout/success/', views.payment_success_view, name='success'),
    path('track/<str:order_id>/', views.track_order_view, name='track'),
]
