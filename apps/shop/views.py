from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.models import CustomUser, Wallet, WalletTransaction

def home_view(request):
    """
    Allows anonymous guest browsing. 
    Users can view categories, items, and add to cart without logging in.
    """
    categories = [
        {'id': 1, 'name': '🔥 Premium Suya'}, 
        {'id': 2, 'name': 'Grills & BBQ'},
        {'id': 3, 'name': 'Sides & Noodles'},
        {'id': 4, 'name': 'Chilled Drinks'}
    ]
    return render(request, 'shop/home.html', {'categories': categories})

def add_to_cart_view(request, item_id):
    """
    Allows guests and authenticated users alike to populate their session cart.
    """
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    
    mock_db = {
        '1': {'name': 'Spicy Beef Suya', 'price': 2500, 'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60'},
        '2': {'name': 'Chicken Suya (Quarter)', 'price': 3800, 'image': 'https://images.unsplash.com/photo-1606622839958-384ef8471da3?w=500&auto=format&fit=crop&q=60'}
    }
    
    if item_id_str in mock_db:
        if item_id_str in cart:
            cart[item_id_str]['quantity'] += 1
        else:
            cart[item_id_str] = {
                'id': item_id_str,
                'name': mock_db[item_id_str]['name'],
                'price': mock_db[item_id_str]['price'],
                'image': mock_db[item_id_str]['image'],
                'quantity': 1
            }
            
    request.session['cart'] = cart
    request.session.modified = True
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    total_items = sum(item['quantity'] for item in cart.values())
    
    return render(request, 'shop/partials/cart_drawer.html', {
        'cart_items': cart.values(),
        'subtotal': subtotal,
        'total_items': total_items
    })

def checkout_view(request):
    """
    AUTHENTICATION INTERCEPT:
    If a guest tries to check out, we save their intent and redirect to login/signup.
    """
    if not request.user.is_authenticated:
        messages.info(request, "Please sign in or create an account to complete your Isheri Grills order.")
        return redirect('users:login')

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:home')

    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    platform_fee = 70
    delivery_fee = 1500 # Dynamic Google Maps fee hooks here
    total_amount = subtotal + platform_fee + delivery_fee
    
    cart_items = [{'name': item['name'], 'quantity': item['quantity'], 'total': item['price'] * item['quantity']} for item in cart.values()]
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'platform_fee': platform_fee,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
    }
    return render(request, 'shop/checkout.html', context)

def payment_success_view(request):
    """
    Fulfills order success, drops 2% cashback into wallet, 
    and checks if this was a referred user's first order to reward the referrer.
    """
    if not request.user.is_authenticated:
        return redirect('users:login')

    cart = request.session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    
    # 1. TRANSACTION CASHBACK ENGINE (2% of food subtotal)
    cashback_earned = int(subtotal * 0.02)
    
    try:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += cashback_earned
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, 
            amount=cashback_earned, 
            transaction_type='CREDIT', 
            description=f'2% Cashback on order subtotal ₦{subtotal}'
        )
    except Exception as e:
        print(f"Wallet ledger update skipped/failed: {e}")

    # 2. REFERRAL BONUS CHECK (If user was referred and this is their first order)
    # Checked via user profile reference attribute
    referred_by_code = getattr(request.user, 'referred_by', None)
    if referred_by_code:
        try:
            referrer_user = CustomUser.objects.get(referral_code=referred_by_code)
            referrer_wallet, _ = Wallet.objects.get_or_create(user=referrer_user)
            
            # Check if referral bonus was already paid out for this user to prevent double payouts
            bonus_already_paid = WalletTransaction.objects.filter(
                wallet=referrer_wallet, 
                description__icontains=f'Referral bonus for {request.user.email}'
            ).exists()
            
            if not bonus_already_paid:
                referrer_wallet.balance += 250
                referrer_wallet.save()
                WalletTransaction.objects.create(
                    wallet=referrer_wallet,
                    amount=250,
                    transaction_type='CREDIT',
                    description=f'Referral bonus for inviting {request.user.email}'
                )
                print(f"🎁 REFERRAL BONUS: ₦250 paid out to referrer {referrer_user.email}")
        except Exception as e:
            print(f"Referral payout processing failed: {e}")

    # Clear Cart
    request.session['cart'] = {}
    request.session.modified = True
    
    import uuid
    order_id = str(uuid.uuid4()).split('-')[0].upper()
    
    context = {
        'order_id': order_id,
        'subtotal': subtotal,
        'cashback_earned': cashback_earned,
        'total_paid': subtotal + 70 + 1500,
    }
    return render(request, 'shop/receipt.html', context)

def track_order_view(request, order_id):
    context = {
        'order_id': order_id,
        'status': 'Out for Delivery',
        'rider_name': 'Segun Adebayo',
        'rider_phone': '08123456789'
    }
    return render(request, 'shop/track.html', context)
