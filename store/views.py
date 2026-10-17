from django.shortcuts import render
from . models import Category, Product

# Create your views here.
def home_view(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured = True)[:4]
    new_arrivals = Product.objects.all()[:4]
    return render(request,'store_template/home.html',{'categories' : categories,'featured_products' : featured_products, 'new_arrivals' : new_arrivals})