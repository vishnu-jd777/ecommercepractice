from . models import Category, Wishlist

def categories(request):
    return {'nav_categories' : Category.objects.all()}

def wishlist_ids(request):
    if request.user.is_authenticated:
        ids = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list('product_id', flat=True)
        )
    else:
        ids = set()

    return {'wishlist_ids': ids}