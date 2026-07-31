from django.shortcuts import render, redirect

def kitchen_dashboard_view(request):
    return render(request, 'shop/kitchen_dashboard.html')

def update_order_status_view(request, order_number):
    return redirect('shop:kitchen_dashboard')
