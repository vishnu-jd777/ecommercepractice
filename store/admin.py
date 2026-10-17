from django.contrib import admin
from . models import Category, Product

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