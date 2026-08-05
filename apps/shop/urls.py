from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.landing_view, name='home'),
    path('menu/', views.menu_view, name='menu'),
    path('category/<int:category_id>/', views.category_view, name='category'),
    path('product/<int:item_id>/', views.product_view, name='product'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/initialize/', views.initialize_payment_view, name='initialize_payment'),
    path('cart/add/<int:item_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('checkout/success/', views.payment_success_view, name='success'),
    path('track/<str:order_id>/', views.track_order_view, name='track'),
    path('review/submit/', views.submit_review_view, name='submit_review'),
]
