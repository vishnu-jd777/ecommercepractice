from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Address
from cart.models import Cart, CartItem
from store.models import Category, Product

from .models import Order, OrderItem

User = get_user_model()


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')

        self.address = Address.objects.create(
            user=self.user, full_name='Test Buyer', phone='9999999999',
            address_line='12 Main Road', city='Kochi', state='Kerala',
            pincode='682001',
        )

        category = Category.objects.create(name='Mobiles', slug='mobiles')
        self.phone = Product.objects.create(
            category=category, name='Test Phone', slug='test-phone',
            brand='Samsung', price=20000, stock=5,
            description='Test description', specs='One\nTwo',
        )
        self.cable = Product.objects.create(
            category=category, name='Test Cable', slug='test-cable',
            brand='Anker', price=1000, stock=3,
            description='Test description', specs='One\nTwo',
        )

        # A cart worth 2 x 20000 + 1 x 1000 = 41000
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.phone, quantity=2)
        CartItem.objects.create(cart=cart, product=self.cable, quantity=1)

        self.client.login(username='buyer', password='pass12345')
        self.checkout_url = reverse('orders:checkout')

    def place_order(self):
        return self.client.post(self.checkout_url, {'address': self.address.id})

    def make_order(self, user=None, status='PLACED'):
        user = user or self.user
        order = Order.objects.create(
            user=user, full_name='Test Buyer', phone='9999999999',
            address_line='12 Main Road', city='Kochi', state='Kerala',
            pincode='682001', total_amount=40000, status=status,
        )
        OrderItem.objects.create(
            order=order, product=self.phone, product_name=self.phone.name,
            price=self.phone.price, quantity=2,
        )
        return order

    # ---------- Checkout ----------
    def test_checkout_requires_login(self):
        self.client.logout()
        response = self.client.get(self.checkout_url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={self.checkout_url}",
            fetch_redirect_response=False,
        )

    def test_empty_cart_redirects_to_cart(self):
        CartItem.objects.all().delete()
        response = self.client.get(self.checkout_url)
        self.assertRedirects(
            response, reverse('cart:cart_detail'), fetch_redirect_response=False
        )

    def test_no_address_redirects_to_add_address_and_back(self):
        self.address.delete()
        response = self.client.get(self.checkout_url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:add_address')}?next={self.checkout_url}",
            fetch_redirect_response=False,
        )

    def test_checkout_page_shows_address_and_total(self):
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Buyer')
        self.assertContains(response, 'Cash on Delivery')

    def test_place_order_creates_order_and_updates_stock_and_cart(self):
        response = self.place_order()
        order = Order.objects.get()

        self.assertRedirects(
            response, reverse('orders:order_success', args=[order.id]),
            fetch_redirect_response=False,
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'PLACED')
        self.assertEqual(order.total_amount, 41000)
        self.assertEqual(order.city, 'Kochi')
        self.assertEqual(order.items.count(), 2)

        phone_line = order.items.get(product=self.phone)
        self.assertEqual(phone_line.product_name, 'Test Phone')
        self.assertEqual(phone_line.price, 20000)
        self.assertEqual(phone_line.quantity, 2)

        self.phone.refresh_from_db()
        self.cable.refresh_from_db()
        self.assertEqual(self.phone.stock, 3)     # 5 - 2
        self.assertEqual(self.cable.stock, 2)     # 3 - 1
        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 0)

    def test_order_blocked_when_stock_is_not_enough(self):
        self.phone.stock = 1                       # cart wants 2
        self.phone.save()
        self.place_order()

        self.assertEqual(Order.objects.count(), 0)
        self.phone.refresh_from_db()
        self.assertEqual(self.phone.stock, 1)
        self.assertEqual(CartItem.objects.filter(cart__user=self.user).count(), 2)

    def test_cannot_order_to_another_users_address(self):
        theirs = Address.objects.create(
            user=self.other, full_name='Someone Else', phone='8888888888',
            address_line='Other Street', city='Delhi', state='Delhi',
            pincode='110001',
        )
        response = self.client.post(self.checkout_url, {'address': theirs.id})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_keeps_snapshot_after_address_and_price_change(self):
        self.place_order()
        self.address.city = 'Delhi'
        self.address.save()
        self.phone.price = 99999
        self.phone.save()

        order = Order.objects.get()
        self.assertEqual(order.city, 'Kochi')
        self.assertEqual(order.items.get(product=self.phone).price, 20000)

    def test_success_page_only_for_owner(self):
        theirs = self.make_order(user=self.other)
        response = self.client.get(reverse('orders:order_success', args=[theirs.id]))
        self.assertEqual(response.status_code, 404)

    # ---------- Order list and detail ----------
    def test_order_list_shows_only_own_orders(self):
        mine = self.make_order()
        self.make_order(user=self.other)
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([o.id for o in response.context['orders']], [mine.id])

    def test_order_detail_shows_items(self):
        order = self.make_order()
        response = self.client.get(reverse('orders:order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Phone')
        self.assertContains(response, f'Order #{order.id}')

    def test_order_detail_of_another_user_is_404(self):
        theirs = self.make_order(user=self.other)
        response = self.client.get(reverse('orders:order_detail', args=[theirs.id]))
        self.assertEqual(response.status_code, 404)

    # ---------- Cancel ----------
    def test_cancel_placed_order_restores_stock(self):
        order = self.make_order()
        self.phone.stock = 3                       # as if 2 had been sold
        self.phone.save()

        self.client.post(reverse('orders:cancel_order', args=[order.id]))

        order.refresh_from_db()
        self.phone.refresh_from_db()
        self.assertEqual(order.status, 'CANCELLED')
        self.assertEqual(self.phone.stock, 5)

    def test_cannot_cancel_after_shipping(self):
        order = self.make_order(status='SHIPPED')
        self.phone.stock = 3
        self.phone.save()

        self.client.post(reverse('orders:cancel_order', args=[order.id]))

        order.refresh_from_db()
        self.phone.refresh_from_db()
        self.assertEqual(order.status, 'SHIPPED')
        self.assertEqual(self.phone.stock, 3)

    def test_cancel_requires_post(self):
        order = self.make_order()
        response = self.client.get(reverse('orders:cancel_order', args=[order.id]))
        self.assertEqual(response.status_code, 405)

    def test_cannot_cancel_another_users_order(self):
        theirs = self.make_order(user=self.other)
        response = self.client.post(reverse('orders:cancel_order', args=[theirs.id]))
        self.assertEqual(response.status_code, 404)
        theirs.refresh_from_db()
        self.assertEqual(theirs.status, 'PLACED')

    # ---------- Model rules ----------
    def test_can_cancel_and_status_step_rules(self):
        placed = self.make_order(status='PLACED')
        shipped = self.make_order(status='SHIPPED')
        out = self.make_order(status='OUT_FOR_DELIVERY')
        delivered = self.make_order(status='DELIVERED')
        cancelled = self.make_order(status='CANCELLED')

        self.assertTrue(placed.can_cancel)
        for order in (shipped, out, delivered, cancelled):
            self.assertFalse(order.can_cancel)

        self.assertEqual(
            [o.status_step for o in (placed, shipped, out, delivered, cancelled)],
            [1, 2, 3, 4, 0],
        )