from django.shortcuts import render, redirect

def admin_analytics_view(request):
    return render(request, 'shop/analytics.html')

def toggle_item_availability_view(request, item_id):
    return redirect('shop:admin_analytics')
