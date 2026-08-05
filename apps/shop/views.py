import random
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, MenuItem, PromoBanner, Order, OrderItem, DeliverySignature
from apps.users.models import CustomUser, Wallet, WalletTransaction
from apps.users.emails import send_order_receipt

def landing_view(request):
    """A branded landing experience shown at the app root."""
    categories = Category.objects.order_by('display_order', 'name')[:4]
    promos = PromoBanner.objects.filter(is_active=True).order_by('display_order')[:6]
    return render(request, 'shop/landing.html', {'categories': categories, 'promos': promos})


def menu_view(request):
    categories = Category.objects.order_by('display_order', 'name').prefetch_related('items')
    return render(request, 'shop/menu.html', {'categories': categories})


def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = category.items.filter(is_available=True)
    return render(request, 'shop/category.html', {
        'category': category,
        'items': items,
    })


def product_view(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    return render(request, 'shop/product.html', {'item': item})


def add_to_cart_view(request, item_id):
    """
    Allows guests and authenticated users alike to populate their session cart.
    """
    cart = request.session.get('cart', {})
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    item_id_str = str(item_id)
    price = float(item.price)
    image_url = item.image.url if item.image else 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=500&q=60'

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += 1
    else:
        cart[item_id_str] = {
            'id': item.id,
            'name': item.name,
            'price': price,
            'image': image_url,
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
    checkout_details = request.session.get('checkout_details', {})

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'platform_fee': platform_fee,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'checkout_details': checkout_details,
    }
    return render(request, 'shop/checkout.html', context)


def initialize_payment_view(request):
    """Accept checkout details and route the user into the success flow."""
    if not request.user.is_authenticated:
        messages.info(request, "Please sign in or create an account to complete your Isheri Grills order.")
        return redirect('users:login')

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:home')

    if request.method != 'POST':
        return redirect('shop:checkout')

    delivery_address = request.POST.get('delivery_address', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()

    if not delivery_address:
        messages.error(request, 'Please add a delivery address to continue.')
        return redirect('shop:checkout')

    if phone_number:
        request.user.phone_number = phone_number
        request.user.save(update_fields=['phone_number'])

    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    total_amount = subtotal + 70 + 1500

    request.session['checkout_details'] = {
        'address': delivery_address,
        'phone_number': phone_number,
        'subtotal': subtotal,
        'total_amount': total_amount,
    }
    request.session.modified = True

    messages.success(request, 'Your order details were captured successfully.')
    return redirect('shop:success')


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

    checkout_details = request.session.get('checkout_details', {})
    delivery_address = checkout_details.get('address', 'Delivery address not provided')
    phone_number = checkout_details.get('phone_number', '')

    order_number = str(uuid.uuid4()).split('-')[0].upper()
    order = Order.objects.create(
        order_number=order_number,
        user=request.user,
        subtotal=subtotal,
        delivery_fee=1500,
        customer_platform_fee=70,
        total_amount=subtotal + 70 + 1500,
        delivery_address=delivery_address,
        status='Pending',
    )

    for item_data in cart.values():
        item = MenuItem.objects.get(id=item_data['id'])
        OrderItem.objects.create(
            order=order,
            item=item,
            price=item_data['price'],
            quantity=item_data['quantity'],
        )

    signature = DeliverySignature.objects.create(
        order=order,
        qr_payload=f"isheri://order/{order_number}",
        customer_pin=f"{random.randint(100000, 999999)}",
        rider_pin=f"{random.randint(100000, 999999)}",
    )

    context = {
        'order_id': order_number,
        'subtotal': subtotal,
        'cashback_earned': cashback_earned,
        'total_paid': subtotal + 70 + 1500,
        'address': delivery_address,
        'phone_number': phone_number,
        'customer_pin': signature.customer_pin,
        'qr_payload': signature.qr_payload,
    }

    # Send order receipt email to the customer (best-effort)
    try:
        send_order_receipt(request.user.email, request.user.full_name, context)
    except Exception as e:
        print(f"Order receipt email failed: {e}")
    return render(request, 'shop/receipt.html', context)

def track_order_view(request, order_id):
    context = {
        'order_id': order_id,
        'status': 'Out for Delivery',
        'rider_name': 'Segun Adebayo',
        'rider_phone': '08123456789'
    }
    return render(request, 'shop/track.html', context)


def submit_review_view(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('shop:home')

    order_id = request.POST.get('order_id')
    rating = int(request.POST.get('rating', 0))
    feedback = request.POST.get('feedback', '').strip()

    from .models import DeliveryReview

    if not order_id or rating <= 0:
        return redirect('shop:home')

    try:
        DeliveryReview.objects.create(order_id=order_id, user=request.user, rating=rating, feedback=feedback)
    except Exception as e:
        print(f"Failed to save review: {e}")

    # Thank you fragment
    return render(request, 'shop/partials/review_thanks.html', {'rating': rating})
