from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import random

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    prep_time = models.PositiveIntegerField(default=20, help_text="Preparation time in minutes")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5, 
                                 validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    is_featured = models.BooleanField(default=False, help_text="Show in Hero Promo Carousel")
    promo_text = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Special Weekend Discount!")

    def __str__(self): return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        self.save()
        return otp

    def __str__(self): return f"{self.user.username}'s Profile"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid/Received'),
        ('Preparing', 'Preparing 🍳'),
        ('Out for Delivery', 'Out for Delivery 🚚'),
        ('Delivered', 'Delivered ✅'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=70.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
