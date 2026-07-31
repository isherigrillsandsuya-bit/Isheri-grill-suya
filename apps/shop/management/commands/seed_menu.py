from django.core.management.base import BaseCommand
from apps.shop.models import Category, MenuItem

class Command(BaseCommand):
    help = 'Seeds the database with the exact ISHERI GRILLS & SUYA menu'
    def handle(self, *args, **kwargs):
        self.stdout.write("🔥 Seeding Isheri Grills & Suya Menu...")
        pasta_cat, _ = Category.objects.get_or_create(name="PASTA", slug="pasta", display_order=1)
        shawarma_cat, _ = Category.objects.get_or_create(name="SHAWARMA", slug="shawarma", display_order=2)
        grills_cat, _ = Category.objects.get_or_create(name="GRILLS", slug="grills", display_order=3)
        extra_cat, _ = Category.objects.get_or_create(name="EXTRA", slug="extra", display_order=4)

        menu_data = [
            (pasta_cat, "Pasta And Chicken", 6000), (pasta_cat, "Pasta And Turkey", 7000),
            (pasta_cat, "Pasta And Two Beef", 4000), (shawarma_cat, "Chicken Plain", 2000),
            (shawarma_cat, "Single Sausage", 2500), (shawarma_cat, "Double Sausage", 3000),
            (shawarma_cat, "Chicken Filled", 3500), (shawarma_cat, "Jumbo Size", 5000),
            (grills_cat, "Chicken And Chips", 7000), (grills_cat, "Turkey And Chips", 8000),
            (grills_cat, "Croaker Fish & Chips", 12000), (extra_cat, "Chicken", 4000),
            (extra_cat, "Turkey", 5000), (extra_cat, "Beef", 1000),
            (extra_cat, "Coleslaw", 1000), (extra_cat, "Sausage", 500),
        ]
        for category, name, price in menu_data:
            item, created = MenuItem.objects.get_or_create(category=category, name=name, defaults={'price': price})
            if created: self.stdout.write(self.style.SUCCESS(f"Added: {name} (₦{price:,.2f})"))
            else: self.stdout.write(f"Already exists: {name}")
        self.stdout.write(self.style.SUCCESS("✅ All 16 Menu Items Successfully Seeded!"))
