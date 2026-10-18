from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from store.models import Product
from .models import Cart, CartItem


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.in_stock:
        messages.error(request, 'Sorry, this item is out of stock.')
        return redirect('store:product_detail', slug=product.slug)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.error(
                request,
                f'Only {product.stock} units are available.'
            )
            return redirect('store:product_detail', slug=product.slug)

    messages.success(request, f'{product.name} added to your cart.')
    return redirect('store:product_detail', slug=product.slug)