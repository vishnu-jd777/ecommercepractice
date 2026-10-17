from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product

CATEGORIES = [
    ('Mobiles', '📱'),
    ('Laptops', '💻'),
    ('Headphones', '🎧'),
    ('Smartwatches', '⌚'),
    ('Accessories', '🔌'),
]

# (category, name, brand, price, stock, featured, description, specs)
PRODUCTS = [
    ('Mobiles', 'Galaxy S24 5G 128GB', 'Samsung', 64999, 15, True, 'Flagship phone with a bright AMOLED display and a pro-grade camera.', '6.2 inch AMOLED\n8GB RAM, 128GB storage\n50MP triple camera\n4000 mAh battery'),
    ('Mobiles', 'Galaxy A55 5G', 'Samsung', 32999, 25, False, 'Mid-range phone with a smooth display and long software support.', '6.6 inch Super AMOLED\n8GB RAM, 128GB storage\n50MP camera\n5000 mAh battery'),
    ('Mobiles', 'iPhone 15 128GB', 'Apple', 69999, 10, True, 'Dynamic Island, USB-C and a great 48MP camera.', '6.1 inch OLED\nA16 Bionic chip\n48MP main camera\nUSB-C charging'),
    ('Mobiles', 'Redmi Note 13 Pro', 'Xiaomi', 24999, 40, False, 'Big battery and a 200MP camera at a friendly price.', '6.67 inch AMOLED\n8GB RAM, 256GB storage\n200MP camera\n67W fast charging'),
    ('Mobiles', 'OnePlus 12R', 'OnePlus', 39999, 0, False, 'Fast performance with a huge battery and quick charging.', '6.78 inch AMOLED 120Hz\n8GB RAM, 128GB storage\n5500 mAh battery\n100W charging'),
    ('Mobiles', 'Pixel 8a', 'Google', 52999, 12, False, 'Clean Android, excellent camera and 7 years of updates.', '6.1 inch OLED 120Hz\nTensor G3 chip\n64MP camera\n7 years of updates'),

    ('Laptops', 'MacBook Air M2 13"', 'Apple', 99900, 8, True, 'Thin, silent and fast with all-day battery life.', 'Apple M2 chip\n8GB RAM, 256GB SSD\n13.6 inch Retina display\nUp to 18 hours battery'),
    ('Laptops', 'Pavilion 15 Core i5', 'HP', 58990, 14, False, 'Reliable everyday laptop for study and office work.', 'Intel Core i5 13th Gen\n16GB RAM, 512GB SSD\n15.6 inch Full HD\nWindows 11'),
    ('Laptops', 'IdeaPad Slim 3', 'Lenovo', 44990, 20, False, 'Light and affordable laptop for students.', 'Ryzen 5 processor\n8GB RAM, 512GB SSD\n15.6 inch Full HD\nWindows 11'),
    ('Laptops', 'TUF Gaming F15', 'Asus', 74990, 6, True, 'Gaming laptop with a dedicated RTX graphics card.', 'Intel Core i7\nRTX 4050 6GB graphics\n16GB RAM, 512GB SSD\n144Hz display'),
    ('Laptops', 'Inspiron 14', 'Dell', 52990, 0, False, 'Compact laptop with a sturdy build and good keyboard.', 'Intel Core i5\n16GB RAM, 512GB SSD\n14 inch Full HD\nBacklit keyboard'),

    ('Headphones', 'WH-1000XM5', 'Sony', 29990, 18, True, 'Industry-leading noise cancelling over-ear headphones.', 'Active noise cancelling\n30 hours battery\nBluetooth 5.2\nFast USB-C charging'),
    ('Headphones', 'AirPods Pro 2', 'Apple', 24900, 22, False, 'Earbuds with strong noise cancelling and clear calls.', 'Active noise cancelling\nUSB-C case\n6 hours listening time\nSweat and dust resistant'),
    ('Headphones', 'Rockerz 450', 'boAt', 1499, 80, False, 'Budget wireless headphones with punchy bass.', '15 hours battery\nBluetooth 5.0\n40mm drivers\nFoldable design'),
    ('Headphones', 'Buds Core R100', 'OnePlus', 1999, 60, False, 'Light true wireless earbuds for daily use.', '20 hours with case\nBluetooth 5.3\nDual microphones\nIP55 water resistance'),
    ('Headphones', 'Soundcore Q30', 'Anker', 5999, 30, False, 'Hybrid noise cancelling with very long battery life.', 'Hybrid noise cancelling\n40 hours battery\nBluetooth 5.0\nMultiple ANC modes'),

    ('Smartwatches', 'Watch Series 9', 'Apple', 41900, 9, True, 'Bright always-on display with advanced health tracking.', 'Always-on Retina display\nHeart rate and ECG\nGPS\nUp to 18 hours battery'),
    ('Smartwatches', 'Galaxy Watch6', 'Samsung', 22999, 16, False, 'Stylish smartwatch with sleep and fitness tracking.', '1.5 inch AMOLED\nSleep coaching\nGPS\nWater resistant'),
    ('Smartwatches', 'Fire-Boltt Ninja', 'Fire-Boltt', 1799, 70, False, 'Affordable fitness band with many sport modes.', '1.83 inch display\n100+ sports modes\nSpO2 monitoring\n7 days battery'),
    ('Smartwatches', 'Band 8 Pro', 'Xiaomi', 4499, 35, False, 'Slim fitness tracker with a large bright screen.', '1.74 inch AMOLED\nBuilt-in GPS\n14 days battery\n150+ workout modes'),

    ('Accessories', 'Nano Power Bank 20000mAh', 'Mi', 1999, 55, False, 'Fast charging power bank that charges two devices at once.', '20000 mAh\n22.5W fast charging\nDual USB ports\nType-C input'),
    ('Accessories', 'Wireless Mouse M331', 'Logitech', 899, 90, False, 'Silent clicks and a comfortable shape for daily work.', 'Silent buttons\n2.4 GHz wireless\n18 months battery\nCompact design'),
    ('Accessories', 'Mechanical Keyboard K2', 'Keychron', 8499, 11, True, 'Compact wireless mechanical keyboard for Mac and Windows.', '75 percent layout\nBluetooth and wired\nHot-swappable switches\nRGB backlight'),
    ('Accessories', '65W GaN Fast Charger', 'Ambrane', 1299, 0, False, 'Charges your phone and laptop with one small adapter.', '65W output\nGaN technology\nUSB-C and USB-A ports\nOver-heat protection'),
    ('Accessories', 'USB-C Hub 7-in-1', 'Anker', 3499, 28, False, 'Adds HDMI, USB and card slots to your laptop.', '4K HDMI\n3 USB ports\nSD and microSD slots\n100W power pass-through'),
]


class Command(BaseCommand):
    help = 'Adds sample categories and 25 sample products'

    def handle(self, *args, **options):
        cats = {}
        for name, icon in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon},
            )
            cats[name] = cat

        created = 0
        for cat_name, name, brand, price, stock, featured, desc, specs in PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    'category': cats[cat_name],
                    'name': name,
                    'brand': brand,
                    'price': price,
                    'stock': stock,
                    'is_featured': featured,
                    'description': desc,
                    'specs': specs,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Done. {created} new products added.'))