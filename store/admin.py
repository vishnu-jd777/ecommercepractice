from django.contrib import admin
from . models import Category, Product, Wishlist, Review

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug','icon')
    prepopulated_fields = { 'slug' : ('name',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','brand','price','stock','is_featured',)
    list_filter = ('category','is_featured')
    search_fields = ('name','brand')
    list_editable = ('price','stock','is_featured')
    prepopulated_fields = { 'slug' : ('name',)}

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)

