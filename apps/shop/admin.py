from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, Wallet, WalletTransaction, PromoBanner

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)


@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
	list_display = ('title', 'discount_percent', 'is_active', 'display_order', 'start_date', 'end_date')
	list_filter = ('is_active',)
	search_fields = ('title', 'subtitle')
	ordering = ('display_order', '-created_at')


from .models import DeliveryReview


@admin.register(DeliveryReview)
class DeliveryReviewAdmin(admin.ModelAdmin):
	list_display = ('order_id', 'user', 'rating', 'created_at')
	search_fields = ('order_id', 'user__email')
	readonly_fields = ('created_at',)

from .models import DeliverySignature


@admin.register(DeliverySignature)
class DeliverySignatureAdmin(admin.ModelAdmin):
	list_display = ('order', 'customer_confirmed', 'rider_confirmed', 'created_at')
	readonly_fields = ('created_at', 'updated_at')
