from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction

from cart.models import Cart
from accounts.models import Address
from .models import Order, OrderItem

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    # Step 1: Check whether the cart is empty
    if not items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    # Step 2: Get the user's saved addresses
    addresses = request.user.addresses.all()

    if not addresses.exists():
        messages.error(
            request,
            'Please add a delivery address to continue.'
        )
        return redirect(
            f"{reverse('accounts:add_address')}?"
            f"next={reverse('orders:checkout')}"
        )

    # Step 3: Process the order when the form is submitted
    if request.method == 'POST':

        address = get_object_or_404(
            Address,
            id=request.POST.get('address'),
            user=request.user
        )

        # Check stock before creating the order
        for item in items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f"Only {item.product.stock} units of "
                    f"{item.product.name} are available."
                )
                return redirect('cart:cart_detail')

        # Create the order as one atomic operation
        with transaction.atomic():

            order = Order.objects.create(
                user=request.user,
                full_name=address.full_name,
                phone=address.phone,
                address_line=address.address_line,
                city=address.city,
                state=address.state,
                pincode=address.pincode,
                total_amount=cart.total_price
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )

                item.product.stock -= item.quantity
                item.product.save()

            # Empty the cart after creating the order items
            cart.items.all().delete()

        return redirect(
            'orders:order_success',
            order_id=order.id
        )

    # Step 4: Display checkout for a GET request
    return render(
        request,
        'orders_templates/checkout.html',
        {
            'cart': cart,
            'items': items,
            'addresses': addresses
        }
    )

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'orders_templates/order_success.html',
        {'order': order}
    )