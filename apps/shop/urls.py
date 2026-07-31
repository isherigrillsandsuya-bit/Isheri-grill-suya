from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('menu/', views.menu_view, name='menu'),
    path('category/<int:cat_id>/', views.category_view, name='category'),
    path('profile/', views.profile_view, name='profile'),
]
