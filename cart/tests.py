from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product

from .models import Cart, CartItem

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')

        category = Category.objects.create(name='Mobiles', slug='mobiles')
        self.phone = Product.objects.create(
            category=category, name='Test Phone', slug='test-phone',
            brand='Samsung', price=20000, stock=5,
            description='Test description', specs='One\nTwo',
        )
        self.sold_out = Product.objects.create(
            category=category, name='Sold Out Phone', slug='sold-out-phone',
            brand='Apple', price=50000, stock=0,
            description='Test description', specs='One\nTwo',
        )
        self.cable = Product.objects.create(
            category=category, name='Test Cable', slug='test-cable',
            brand='Anker', price=1000, stock=3,
            description='Test description', specs='One\nTwo',
        )

        self.client.login(username='tester', password='pass12345')

    def add_url(self, product):
        return reverse('cart:add_to_cart', args=[product.id])

    def make_item(self, product, quantity, user=None):
        cart, _ = Cart.objects.get_or_create(user=user or self.user)
        return CartItem.objects.create(cart=cart, product=product, quantity=quantity)

    # ---------- Add to cart ----------
    def test_add_requires_login(self):
        self.client.logout()
        url = self.add_url(self.phone)
        response = self.client.post(url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_requires_post(self):
        response = self.client.get(self.add_url(self.phone))
        self.assertEqual(response.status_code, 405)

    def test_add_creates_cart_and_item(self):
        self.client.post(self.add_url(self.phone))
        item = CartItem.objects.get(cart__user=self.user, product=self.phone)
        self.assertEqual(item.quantity, 1)

    def test_adding_twice_increases_quantity(self):
        self.client.post(self.add_url(self.phone))
        self.client.post(self.add_url(self.phone))
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_cannot_add_more_than_stock(self):
        for _ in range(5):
            self.client.post(self.add_url(self.cable))   # stock is 3
        self.assertEqual(CartItem.objects.get(product=self.cable).quantity, 3)

    def test_out_of_stock_cannot_be_added(self):
        self.client.post(self.add_url(self.sold_out))
        self.assertEqual(CartItem.objects.count(), 0)

    # ---------- Cart page ----------
    def test_cart_page_requires_login(self):
        self.client.logout()
        url = reverse('cart:cart_detail')
        response = self.client.get(url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_cart_page_shows_items_and_total(self):
        self.make_item(self.phone, 2)     # 2 x 20000
        self.make_item(self.cable, 1)     # 1 x 1000
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Phone')
        self.assertContains(response, 'Test Cable')
        self.assertEqual(response.context['cart'].total_price, 41000)
        self.assertEqual(response.context['cart'].total_items, 3)

    def test_empty_cart_page_loads(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')

    # ---------- Update quantity ----------
    def test_update_quantity(self):
        item = self.make_item(self.phone, 1)
        self.client.post(reverse('cart:update_cart', args=[item.id]), {'quantity': 3})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_update_quantity_is_capped_at_stock(self):
        item = self.make_item(self.phone, 1)      # stock is 5
        self.client.post(reverse('cart:update_cart', args=[item.id]), {'quantity': 99})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_update_to_zero_removes_item(self):
        item = self.make_item(self.phone, 2)
        self.client.post(reverse('cart:update_cart', args=[item.id]), {'quantity': 0})
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_update_with_invalid_value_changes_nothing(self):
        item = self.make_item(self.phone, 2)
        self.client.post(reverse('cart:update_cart', args=[item.id]), {'quantity': 'abc'})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    # ---------- Remove ----------
    def test_remove_item(self):
        item = self.make_item(self.phone, 2)
        self.client.post(reverse('cart:remove_from_cart', args=[item.id]))
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    # ---------- Privacy ----------
    def test_cannot_change_or_remove_another_users_item(self):
        theirs = self.make_item(self.phone, 2, user=self.other)

        update = self.client.post(
            reverse('cart:update_cart', args=[theirs.id]), {'quantity': 5}
        )
        remove = self.client.post(reverse('cart:remove_from_cart', args=[theirs.id]))

        self.assertEqual(update.status_code, 404)
        self.assertEqual(remove.status_code, 404)
        theirs.refresh_from_db()
        self.assertEqual(theirs.quantity, 2)

    # ---------- Navbar count ----------
    def test_cart_count_in_context(self):
        self.make_item(self.phone, 2)
        self.make_item(self.cable, 1)
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.context['cart_count'], 3)

    def test_cart_count_is_zero_for_guest(self):
        self.client.logout()
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.context['cart_count'], 0)