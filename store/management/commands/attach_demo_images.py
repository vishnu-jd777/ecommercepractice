import os
from itertools import cycle

from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import Product


class Command(BaseCommand):
    help = 'Give every product without a photo one of the images in media/products/'

    def handle(self, *args, **options):
        folder = settings.MEDIA_ROOT / 'products'

        if not folder.exists():
            self.stdout.write(self.style.ERROR('Folder media/products/ not found.'))
            return

        names = sorted(
            name for name in os.listdir(folder)
            if name.lower().endswith(('.jpg', '.jpeg', '.png'))
        )
        if not names:
            self.stdout.write(self.style.ERROR('No images found in media/products/.'))
            return

        images = cycle(names)
        updated = 0
        for product in Product.objects.filter(image=''):
            product.image = f'products/{next(images)}'
            product.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Done. {updated} products updated.'))