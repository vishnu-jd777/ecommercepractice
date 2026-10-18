from django.shortcuts import get_object_or_404, redirect, render
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

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    return render(
        request,
        'cart_templates/cart.html',
        {'cart': cart, 'items': items}
    )

@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    quantity = request.POST.get('quantity', '')

    if not quantity.isdigit():
        messages.error(request, 'Please enter a valid quantity.')
        return redirect('cart:cart_detail')

    quantity = int(quantity)

    if quantity <= 0:
        item.delete()
        messages.success(request, 'Item removed from your cart.')

    elif quantity > item.product.stock:
        item.quantity = item.product.stock
        item.save()
        messages.warning(
            request,
            f'Only {item.product.stock} units are available. Quantity updated.'
        )

    else:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cart quantity updated.')

    return redirect('cart:cart_detail')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    messages.success(request, 'Item removed from your cart.')

    return redirect('cart:cart_detail')