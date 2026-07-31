from django.urls import path
from . import views

app_name = 'logistics'
urlpatterns = [
    path('dashboard/', views.rider_dashboard, name='rider_dashboard'),
    path('deliver/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    path('verify_safe/<int:order_id>/', views.verify_safe_delivery, name='verify_safe'),
]
