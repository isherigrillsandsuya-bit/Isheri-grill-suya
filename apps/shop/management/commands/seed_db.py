from django.core.management.base import BaseCommand
from apps.shop.models import Category, MenuItem

class Command(BaseCommand):
    help = 'Seeds initial menu categories and items for Isheri Grills & Suya'

    def handle(self, *args, **options):
        categories_data = [
            {'name': 'Beef & Chicken Suya', 'slug': 'suya'},
            {'name': 'Smokey Shawarma', 'slug': 'shawarma'},
            {'name': 'Flame-Grilled Chicken & Asun', 'slug': 'grills'},
            {'name': 'Chilled Drinks & Beverages', 'slug': 'drinks'},
        ]

        categories = {}
        for cat in categories_data:
            obj, _ = Category.objects.get_or_create(
                slug=cat['slug'],
                defaults={'name': cat['name']}
            )
            # Update name if category already existed under this slug
            if obj.name != cat['name']:
                obj.name = cat['name']
                obj.save()
            categories[cat['slug']] = obj

        items_data = [
            {'name': 'Special Beef Suya (Full Portion)', 'category': categories['suya'], 'price': 2500, 'description': 'Authentic flame-grilled beef suya seasoned with spicy Yaji powder, fresh onions, and tomatoes.'},
            {'name': 'Chicken Suya Skewers', 'category': categories['suya'], 'price': 3000, 'description': 'Tender grilled chicken breast skewers coated in aromatic suya spice.'},
            {'name': 'Double Sausage Shawarma (Beef & Chicken)', 'category': categories['shawarma'], 'price': 3500, 'description': 'Loaded with grilled chicken strips, double sausages, creamy mayo, and hot sauce.'},
            {'name': 'Asun (Spicy Grilled Goat Meat)', 'category': categories['grills'], 'price': 4000, 'description': 'Peppered grilled goat meat tossed with Scotch bonnet peppers and onions.'},
            {'name': 'Full Grilled Peppered Chicken', 'category': categories['grills'], 'price': 7500, 'description': 'Whole chicken marinated in house spices and slowly grilled to charcoal perfection.'},
            {'name': 'Cold Soft Drinks (50cl)', 'category': categories['drinks'], 'price': 500, 'description': 'Chilled Coca-Cola, Fanta, or Sprite.'},
        ]

        for item in items_data:
            MenuItem.objects.get_or_create(
                name=item['name'],
                category=item['category'],
                defaults={
                    'price': item['price'],
                    'description': item['description'],
                    'is_available': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Isheri Grills & Suya menu database!'))
