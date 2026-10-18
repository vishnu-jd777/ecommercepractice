from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class StoreTests(TestCase):
    def setUp(self):
        # Runs before every test. Builds fake data in a temporary test database.
        self.mobiles = Category.objects.create(name='Mobiles', slug='mobiles')
        self.laptops = Category.objects.create(name='Laptops', slug='laptops')

        self.p1 = Product.objects.create(
            category=self.mobiles, name='Galaxy Phone', slug='galaxy-phone',
            brand='Samsung', price=20000, stock=10,
            description='Test description', specs='One\nTwo',
        )
        self.p2 = Product.objects.create(
            category=self.mobiles, name='Galaxy Ultra', slug='galaxy-ultra',
            brand='Samsung', price=30000, stock=5,
            description='Test description', specs='One\nTwo',
        )
        self.p3 = Product.objects.create(
            category=self.mobiles, name='iPhone Pro', slug='iphone-pro',
            brand='Apple', price=60000, stock=3, is_featured=True,
            description='Test description', specs='One\nTwo',
        )
        self.p4 = Product.objects.create(
            category=self.laptops, name='Pavilion Laptop', slug='pavilion-laptop',
            brand='HP', price=50000, stock=7,
            description='Test description', specs='One\nTwo',
        )
        self.p5 = Product.objects.create(
            category=self.laptops, name='Inspiron Laptop', slug='inspiron-laptop',
            brand='Dell', price=45000, stock=0,
            description='Test description', specs='One\nTwo',
        )

        self.list_url = reverse('store:product_list')

    def names(self, response):
        # Product names on the current page, in the order shown.
        return [p.name for p in response.context['page_obj']]

    # 1. Home page
    def test_home_page_loads_and_shows_featured(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone Pro')

    # 2. Product list
    def test_product_list_loads(self):
        response = self.client.get(self.list_url, {'sort': 'name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 5)

    # 3. Search
    def test_search_filters_products(self):
        response = self.client.get(self.list_url, {'q': 'galaxy', 'sort': 'name'})
        self.assertEqual(self.names(response), ['Galaxy Phone', 'Galaxy Ultra'])

    def test_search_with_no_match_is_empty(self):
        response = self.client.get(self.list_url, {'q': 'zzzzzz'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.names(response), [])

    # 4. Brand filter
    def test_brand_filter(self):
        response = self.client.get(self.list_url, {'brand': 'Samsung', 'sort': 'name'})
        self.assertEqual(self.names(response), ['Galaxy Phone', 'Galaxy Ultra'])

    # 5. Price filter and sort
    def test_price_filter_and_sort_low_to_high(self):
        response = self.client.get(
            self.list_url,
            {'min_price': 25000, 'max_price': 55000, 'sort': 'price_low'},
        )
        self.assertEqual(
            self.names(response),
            ['Galaxy Ultra', 'Inspiron Laptop', 'Pavilion Laptop'],
        )

    def test_sort_high_to_low(self):
        response = self.client.get(self.list_url, {'sort': 'price_high'})
        self.assertEqual(
            self.names(response),
            ['iPhone Pro', 'Pavilion Laptop', 'Inspiron Laptop', 'Galaxy Ultra'],
        )

    def test_bad_price_value_does_not_crash(self):
        response = self.client.get(self.list_url, {'min_price': 'abc', 'max_price': 'xyz'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 5)

    # 6. Category page
    def test_category_page_shows_only_its_products(self):
        url = reverse('store:category', args=['mobiles'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            self.names(response), ['Galaxy Phone', 'Galaxy Ultra', 'iPhone Pro']
        )

    # 7. Pagination (4 per page, 5 products)
    def test_pagination(self):
        page1 = self.client.get(self.list_url)
        page2 = self.client.get(self.list_url, {'page': 2})
        self.assertEqual(len(page1.context['page_obj']), 4)
        self.assertEqual(len(page2.context['page_obj']), 1)

    # 8. Detail page, 404 and stock
    def test_product_detail_loads(self):
        url = reverse('store:product_detail', args=['galaxy-phone'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Galaxy Phone')

    def test_unknown_product_returns_404(self):
        url = reverse('store:product_detail', args=['does-not-exist'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_in_stock_property(self):
        self.assertTrue(self.p1.in_stock)
        self.assertFalse(self.p5.in_stock)