from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.contrib import messages
from .models import MenuItem, Category, Order, OrderItem, UserProfile
from decimal import Decimal

PLATFORM_FEE = Decimal('70.00')

def home(request):
    categories = Category.objects.all()
    items = MenuItem.objects.filter(is_available=True)
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)
    return render(request, 'home.html', {
        'categories': categories, 
        'items': items,
        'featured_items': featured_items
    })

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        profile, created = UserProfile.objects.get_or_create(user=user)
        otp = profile.generate_otp()

        # Send Email OTP
        send_mail(
            'Your Verification OTP - Isheri Grills & Suya',
            f'Hello {user.username},\n\nYour OTP code for verification is: {otp}\n\nThank you!',
            'noreply@isherigrills.com',
            [email],
            fail_silently=True,
        )

        request.session['unverified_user_id'] = user.id
        messages.success(request, f"OTP sent to {email}. Check server console if email backend is active.")
        return redirect('verify_otp')

    return render(request, 'signup.html')

def verify_otp(request):
    user_id = request.session.get('unverified_user_id')
    if not user_id:
        return redirect('signup')

    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        if profile.otp == input_otp:
            profile.is_email_verified = True
            profile.otp = None
            profile.save()
            login(request, user)
            del request.session['unverified_user_id']
            messages.success(request, "Account verified successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid OTP code. Please try again.")

    return render(request, 'verify_otp.html', {'email': user.email})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if hasattr(user, 'profile') and not user.profile.is_email_verified:
                otp = user.profile.generate_otp()
                send_mail(
                    'Your Verification OTP - Isheri Grills & Suya',
                    f'Your OTP code is: {otp}',
                    'noreply@isherigrills.com',
                    [user.email],
                    fail_silently=True,
                )
                request.session['unverified_user_id'] = user.id
                messages.warning(request, "Please verify your email OTP before logging in.")
                return redirect('verify_otp')

            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'profile.html', {'profile': profile, 'orders': orders})

def product_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    return render(request, 'product_detail.html', {'item': item})

def category_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    items = MenuItem.objects.filter(category=category, is_available=True)
    return render(request, 'category.html', {'category': category, 'items': items})

def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    prod_id = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if prod_id in cart:
        cart[prod_id] += quantity
    else:
        cart[prod_id] = quantity
        
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0.00')
    
    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            total = item.price * quantity
            subtotal += total
            cart_items.append({'item': item, 'quantity': quantity, 'total': total})
        except MenuItem.DoesNotExist:
            continue
            
    delivery_fee = Decimal('500.00') if subtotal > 0 else Decimal('0.00')
    grand_total = subtotal + PLATFORM_FEE + delivery_fee if subtotal > 0 else Decimal('0.00')
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'platform_fee': PLATFORM_FEE,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total
    })

@login_required(login_url='/login/')
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')
        
    subtotal = Decimal('0.00')
    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id)
            subtotal += item.price * quantity
        except MenuItem.DoesNotExist:
            continue
            
    delivery_fee = Decimal('500.00')
    grand_total = subtotal + PLATFORM_FEE + delivery_fee

    if request.method == 'POST':
        address = request.POST.get('address', 'Default Address')
        phone = request.POST.get('phone', '08000000000')
        
        order = Order.objects.create(
            user=request.user,
            delivery_address=address,
            phone_number=phone,
            subtotal=subtotal,
            platform_fee=PLATFORM_FEE,
            delivery_fee=delivery_fee,
            total_amount=grand_total,
            status='Paid'
        )
        
        for item_id, quantity in cart.items():
            try:
                item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=quantity,
                    price=item.price
                )
            except MenuItem.DoesNotExist:
                pass
                
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('order_receipt', order_id=order.id)
        
    return render(request, 'checkout.html', {
        'subtotal': subtotal,
        'platform_fee': PLATFORM_FEE,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total
    })

@login_required
def order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'receipt.html', {'order': order})

@login_required
def order_track(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'track.html', {'order': order})
