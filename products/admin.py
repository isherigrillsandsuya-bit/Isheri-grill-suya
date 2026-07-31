from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, UserProfile

admin.site.site_header = "Isheri Grills & Suya Administration Panel"
admin.site.site_title = "Isheri Grills Admin Portal"
admin.site.index_title = "Welcome to Isheri Grills & Suya Admin Panel"

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'prep_time', 'rating', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_featured', 'prep_time', 'rating')

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(UserProfile)
