from django.shortcuts import render, get_object_or_404
from . models import Category, Product

# Create your views here.
def home_view(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured = True)[:4]
    new_arrivals = Product.objects.all()[:4]
    return render(request,'store_template/home.html',{'categories' : categories,'featured_products' : featured_products, 'new_arrivals' : new_arrivals})

def product_list_view(request):
    products = Product.objects.all()
    return render(request,'store_template/product_list.html',{'products' : products, 'title' : 'All Products'})

def category_view(request,slug):
    category = get_object_or_404(Category,slug=slug)
    products = category.products.all()
    return render(request,'store_template/product_list.html',{'products': products, 'title': category.name})

def product_detail_view(request,slug):
    product = get_object_or_404(Product,slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request,'store_template/product_detail.html',{'product':product,'related_products':related_products})

