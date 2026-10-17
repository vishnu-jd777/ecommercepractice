
from django.test import TestCase
from django.urls import reverse
from .models import User, Address


class AccountTests(TestCase):

    def test_signup_creates_user(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'tester',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '9999999999',
            'password1': 'StrongPass#123',
            'password2': 'StrongPass#123',
        })

        self.assertEqual(User.objects.count(), 1)
        self.assertRedirects(response, reverse('store:home'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_own_addresses(self):
        user_a = User.objects.create_user(
            username='a',
            password='pass12345'
        )
        user_b = User.objects.create_user(
            username='b',
            password='pass12345'
        )

        Address.objects.create(
            user=user_a,
            full_name='Alice Home',
            phone='1111111111',
            address_line='Alice Street',
            city='Kochi',
            state='Kerala',
            pincode='682001'
        )

        Address.objects.create(
            user=user_b,
            full_name='Bob Home',
            phone='2222222222',
            address_line='Bob Street',
            city='Thrissur',
            state='Kerala',
            pincode='680001'
        )

        self.client.login(
            username='a',
            password='pass12345'
        )

        response = self.client.get(reverse('accounts:address_list'))

        self.assertContains(response, 'Alice Home')
        self.assertNotContains(response, 'Bob Home')

    def test_cannot_edit_another_users_address(self):
        user_a = User.objects.create_user(
            username='a',
            password='pass12345'
        )
        user_b = User.objects.create_user(
            username='b',
            password='pass12345'
        )

        bob_address = Address.objects.create(
            user=user_b,
            full_name='Bob Home',
            phone='2222222222',
            address_line='Bob Street',
            city='Thrissur',
            state='Kerala',
            pincode='680001'
        )

        self.client.login(
            username='a',
            password='pass12345'
        )

        response = self.client.get(
            reverse('accounts:edit_address', args=[bob_address.pk])
        )

        self.assertEqual(response.status_code, 404)

