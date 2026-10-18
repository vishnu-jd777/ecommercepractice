from .models import Cart


def cart_count(request):
    count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            count = cart.total_items

    return {'cart_count': count}