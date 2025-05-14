from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Product, Orders, Customer, ProductSubcategory, Currency
import json

class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_index_view_status_code(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'catalog/index.html')

class ProductListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_products = 13  # More than the pagination limit
        for product_num in range(number_of_products):
            Product.objects.create(
                english_product_name=f'Product {product_num}',
                list_price=100.00,
                finished_goods_flag=True
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/products/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)

    def test_pagination_is_five(self):
        response = self.client.get(reverse('products'))
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['product_list']), 5)

class OrderStatusUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='12345')
        permission = Permission.objects.get(codename='can_mark_shipped')
        self.user.user_permissions.add(permission)
        self.client.login(username='testuser2', password='12345')

        self.currency = Currency.objects.create(currency_alternate_key='USD', currency_name='United States Dollar')
        self.customer = Customer.objects.create(
            user=self.user, 
            first_name='John', 
            last_name='Doe',
            email_address='johndoe@example.com',
            birth_date='1980-01-01'
        )
        self.product = Product.objects.create(
            english_product_name='Example Product',
            list_price=150.00,
            finished_goods_flag=True
        )
        self.order = Orders.objects.create(
            product=self.product,
            customer=self.customer,
            currency=self.currency,
            order_quantity=10,
            unit_price=100.00
        )

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('update-order-status', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        response = self.client.get(reverse('update-order-status', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_order_if_logged_in(self):
        response = self.client.get(reverse('update-order-status', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)
