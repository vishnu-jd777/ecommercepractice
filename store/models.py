from django.db import models
from django.conf import settings
from django.db.models import Avg

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10,blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True)
    brand = models.CharField(max_length=100)
    description = models.TextField()
    specs = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveBigIntegerField(default=0)
    image = models.ImageField(upload_to='products/',blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0


    @property
    def review_count(self):
        return self.reviews.count()

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} likes {self.product.name}'


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.user.username} rated '
            f'{self.product.name} {self.rating}/5'
        )

    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
