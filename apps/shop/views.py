from django.shortcuts import render
from .models import Category, MenuItem

def home_view(request):
    categories = Category.objects.all()
    products = MenuItem.objects.filter(is_available=True)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'shop/home.html', context)

def menu_view(request):
    from .models import Product, Category
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'shop/menu.html', {'categories': categories, 'products': products})

def category_view(request, cat_id):
    from .models import Product, Category
    category = Category.objects.get(id=cat_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'shop/menu.html', {'category': category, 'products': products, 'categories': categories})
