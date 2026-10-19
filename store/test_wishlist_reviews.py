from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Review, Wishlist

User = get_user_model()


class WishlistReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='fan', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')

        category = Category.objects.create(name='Mobiles', slug='mobiles')
        self.phone = Product.objects.create(
            category=category, name='Test Phone', slug='test-phone',
            brand='Samsung', price=20000, stock=5,
            description='Test description', specs='One\nTwo',
        )
        self.laptop = Product.objects.create(
            category=category, name='Test Laptop', slug='test-laptop',
            brand='HP', price=50000, stock=5,
            description='Test description', specs='One\nTwo',
        )
        self.client.login(username='fan', password='pass12345')

    def toggle_url(self, product):
        return reverse('store:toggle_wishlist', args=[product.id])

    def detail_url(self, product):
        return reverse('store:product_detail', args=[product.slug])

    def review_url(self, product):
        return reverse('store:add_review', args=[product.slug])

    # ---------- Wishlist ----------
    def test_toggle_requires_login(self):
        self.client.logout()
        url = self.toggle_url(self.phone)
        response = self.client.post(url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )
        self.assertEqual(Wishlist.objects.count(), 0)

    def test_toggle_requires_post(self):
        response = self.client.get(self.toggle_url(self.phone))
        self.assertEqual(response.status_code, 405)

    def test_toggle_adds_then_removes(self):
        url = self.toggle_url(self.phone)

        self.client.post(url)
        self.assertTrue(
            Wishlist.objects.filter(user=self.user, product=self.phone).exists()
        )
        self.assertEqual(Wishlist.objects.count(), 1)

        self.client.post(url)
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, product=self.phone).exists()
        )

    def test_toggle_goes_back_to_safe_next_url(self):
        response = self.client.post(
            self.toggle_url(self.phone), {'next': reverse('store:product_list')}
        )
        self.assertRedirects(
            response, reverse('store:product_list'), fetch_redirect_response=False
        )

    def test_toggle_ignores_unsafe_next_url(self):
        response = self.client.post(
            self.toggle_url(self.phone), {'next': 'https://evil.example.com/'}
        )
        self.assertRedirects(
            response, reverse('store:wishlist'), fetch_redirect_response=False
        )

    def test_toggle_unknown_product_is_404(self):
        url = reverse('store:toggle_wishlist', args=[99999])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_wishlist_page_requires_login(self):
        self.client.logout()
        url = reverse('store:wishlist')
        response = self.client.get(url)
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_wishlist_page_shows_only_own_items(self):
        Wishlist.objects.create(user=self.user, product=self.phone)
        Wishlist.objects.create(user=self.other, product=self.laptop)

        response = self.client.get(reverse('store:wishlist'))
        names = [item.product.name for item in response.context['items']]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(names, ['Test Phone'])

    def test_wishlist_ids_in_context(self):
        Wishlist.objects.create(user=self.user, product=self.phone)
        response = self.client.get(reverse('store:home'))
        self.assertIn(self.phone.id, response.context['wishlist_ids'])
        self.assertNotIn(self.laptop.id, response.context['wishlist_ids'])

        self.client.logout()
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.context['wishlist_ids'], set())

    # ---------- Reviews ----------
    def test_add_review_requires_login(self):
        self.client.logout()
        url = self.review_url(self.phone)
        response = self.client.post(url, {'rating': 4, 'comment': 'Nice'})
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={url}",
            fetch_redirect_response=False,
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_add_review_saves_with_user_and_product(self):
        response = self.client.post(
            self.review_url(self.phone), {'rating': 4, 'comment': 'Great phone'}
        )
        self.assertRedirects(
            response, self.detail_url(self.phone), fetch_redirect_response=False
        )
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.phone)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Great phone')

    def test_cannot_review_same_product_twice(self):
        url = self.review_url(self.phone)
        self.client.post(url, {'rating': 5, 'comment': 'First'})
        self.client.post(url, {'rating': 1, 'comment': 'Second'})

        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().comment, 'First')

    def test_invalid_review_is_not_saved(self):
        url = self.review_url(self.phone)
        self.client.post(url, {'rating': 9, 'comment': 'Too many stars'})
        self.client.post(url, {'rating': 3, 'comment': ''})
        self.assertEqual(Review.objects.count(), 0)

    def test_average_rating_and_review_count(self):
        self.assertEqual(self.phone.average_rating, 0)
        self.assertEqual(self.phone.review_count, 0)

        Review.objects.create(product=self.phone, user=self.user, rating=4, comment='Good')
        Review.objects.create(product=self.phone, user=self.other, rating=2, comment='Meh')

        self.assertEqual(self.phone.average_rating, 3.0)
        self.assertEqual(self.phone.review_count, 2)

    def test_delete_own_review(self):
        review = Review.objects.create(
            product=self.phone, user=self.user, rating=4, comment='Good'
        )
        response = self.client.post(reverse('store:delete_review', args=[review.id]))
        self.assertRedirects(
            response, self.detail_url(self.phone), fetch_redirect_response=False
        )
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_cannot_delete_another_users_review(self):
        review = Review.objects.create(
            product=self.phone, user=self.other, rating=4, comment='Good'
        )
        response = self.client.post(reverse('store:delete_review', args=[review.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_detail_page_shows_reviews(self):
        Review.objects.create(
            product=self.phone, user=self.other, rating=5, comment='Loved it'
        )
        response = self.client.get(self.detail_url(self.phone))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Loved it')
        self.assertEqual(len(response.context['reviews']), 1)
        self.assertIsNone(response.context['user_review'])

    def test_guest_sees_login_prompt_on_detail_page(self):
        self.client.logout()
        response = self.client.get(self.detail_url(self.phone))
        self.assertContains(response, 'to write a review')

    def test_stars_property(self):
        review = Review(rating=3)
        self.assertEqual(review.stars, '★★★☆☆')

    def test_database_blocks_duplicate_reviews(self):
        Review.objects.create(product=self.phone, user=self.user, rating=4, comment='A')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    product=self.phone, user=self.user, rating=2, comment='B'
                )