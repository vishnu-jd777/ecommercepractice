from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from . models import Category, Product, Wishlist, Review
from .forms import ReviewForm

from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme


from django.db.models import Q

# Create your views here.
def build_listing(request,products):
    q = request.GET.get('q', '').strip()
    brand = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'newest')
    brands = products.values_list('brand', flat=True).distinct().order_by('brand')
    if q:
        products = products.filter(
        Q(name__icontains=q) |
        Q(brand__icontains=q) |
        Q(description__icontains=q)
    )

    if brand:
        products = products.filter(brand=brand)

    if min_price.isdigit():
        products = products.filter(price__gte=min_price)

    if max_price.isdigit():
        products = products.filter(price__lte=max_price)

    sort_options = {
     'newest': '-created_at',
     'price_low': 'price',
     'price_high': '-price',
     'name': 'name',
     }

    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    query_string = params.urlencode()
    return {
     'page_obj': page_obj,
     'brands': brands,
     'q': q,
     'brand': brand,
     'min_price': min_price,
     'max_price': max_price,
     'sort': sort,
     'query_string': query_string,
    }

def home_view(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured = True)[:4]
    new_arrivals = Product.objects.all()[:4]
    return render(request,'store_template/home.html',{'categories' : categories,'featured_products' : featured_products, 'new_arrivals' : new_arrivals})

def product_list_view(request):
    context = build_listing(request, Product.objects.all())

    if context['q']:
        context['title'] = f'Results for "{context["q"]}"'
    else:
        context['title'] = 'All Products'

    return render(request, 'store_template/product_list.html', context)

def category_view(request,slug):
    
    category = get_object_or_404(Category, slug=slug)

    context = build_listing(request, category.products.all())
    context['title'] = category.name

    return render(request, 'store_template/product_list.html', context)

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug)

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]

    reviews = product.reviews.select_related('user').all()

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    review_form = ReviewForm()

    return render(
        request,
        'store_template/product_detail.html',
        {
            'product': product,
            'related_products': related_products,
            'reviews': reviews,
            'review_form': review_form,
            'user_review': user_review,
        }
    )
@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, 'Added to your wishlist.')
    else:
        item.delete()
        messages.success(request, 'Removed from your wishlist.')

    next_url = request.POST.get('next')

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)

    return redirect('store:wishlist')

@login_required
def wishlist_view(request):
    items = request.user.wishlist_items.select_related('product')

    return render(
        request,
        'store_template/wishlist.html',
        {'items': items}
    )

@login_required
@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if Review.objects.filter(
        product=product,
        user=request.user
    ).exists():
        messages.error(
            request,
            'You have already reviewed this product.'
        )
        return redirect('store:product_detail', slug=slug)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        messages.success(request, 'Your review was submitted.')
    else:
        messages.error(
            request,
            'Please choose a rating and write a comment.'
        )

    return redirect('store:product_detail', slug=slug)


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    slug = review.product.slug
    review.delete()

    messages.success(request, 'Your review was deleted.')

    return redirect('store:product_detail', slug=slug)