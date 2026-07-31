from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, Wallet, WalletTransaction

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
