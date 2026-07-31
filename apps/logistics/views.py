from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.shop.models import Order

@login_required(login_url='users:login')
def rider_dashboard(request):
    # For now, show all active orders to the rider
    active_orders = Order.objects.exclude(status__in=['Delivered', 'Cancelled']).order_by('-created_at')
    return render(request, 'logistics/rider_dashboard.html', {'orders': active_orders})

@login_required(login_url='users:login')
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'Delivered'
        order.save()
        # In a real app, this triggers the rider wallet payout lock!
    return redirect('logistics:rider_dashboard')

@login_required(login_url='users:login')
def verify_safe_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        pin_entered = request.POST.get('delivery_pin', '').strip()
        # The PIN is the last 4 characters of the order reference
        correct_pin = order.order_number[-4:] 
        
        if pin_entered.upper() == correct_pin.upper():
            order.status = 'Delivered'
            order.save()
            # Rider wallet logic goes here!
            return redirect('logistics:rider_dashboard')
        else:
            # Handle wrong PIN (in real app, use messages framework)
            pass
    return redirect('logistics:rider_dashboard')
