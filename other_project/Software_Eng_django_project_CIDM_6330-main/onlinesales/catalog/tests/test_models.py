from django.test import TestCase
from django.utils import timezone
from catalog.models import Orders, Product, Customer, Currency, ProductSubcategory
from django.contrib.auth.models import User
from decimal import Decimal
import uuid
from django.test import TestCase
from datetime import timedelta


class OrdersModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser', password='12345')
        customer = Customer.objects.create(
            user=user, 
            first_name='John', 
            last_name='Doe', 
            email_address='john@example.com', 
            birth_date='1980-05-01'
        )
        currency = Currency.objects.create(
            currency_alternate_key='USD', 
            currency_name='United States Dollar'
        )
        product = Product.objects.create(
            english_product_name='Test Product', 
            standard_cost=100.00, 
            list_price=150.00,
            finished_goods_flag=True
        )
        
        Orders.objects.create(
            product=product,
            customer=customer,
            currency=currency,
            order_date_actual=timezone.now(),
            due_date_actual=timezone.now() + timezone.timedelta(days=1),
            ship_date_actual=timezone.now() + timezone.timedelta(days=2),
            order_quantity=10,
            unit_price=150.00,
            sales_order_number=str(uuid.uuid4())[:8],  
            extended_amount=Decimal('1500.00')  
        )

    def test_order_content(self):
        order = Orders.objects.get(id=1)
        self.assertIsNotNone(order.sales_order_number, "Sales order number should not be None")
        self.assertTrue(len(order.sales_order_number) > 0, "Sales order number should not be empty")
        self.assertIsNone(order.sales_order_line_number, "Sales order line number should be None if not set")

    def test_order_total_cost(self):
        order = Orders.objects.get(id=1)
        total_cost = Decimal('1500.00')
        self.assertEqual(order.extended_amount, total_cost)

class CustomerModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='customeruser', password='testpass123')
        Customer.objects.create(
            user=user, 
            first_name='Jane', 
            last_name='Smith', 
            email_address='jane@example.com', 
            birth_date='1990-04-01'
        )

    def test_customer_creation(self):
        customer = Customer.objects.get(id=1)
        self.assertTrue(isinstance(customer.user, User))
        self.assertEqual(customer.__str__(), 'Jane Smith')


class ProductModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creating a product subcategory for use in product tests
        cls.subcategory = ProductSubcategory.objects.create(
            english_product_subcategory_name="Electronics",
            spanish_product_subcategory_name="Electrónica",
            french_product_subcategory_name="Électronique"
        )

        # Creating a product instance
        Product.objects.create(
            product_alternate_key='XYZ123',
            product_subcategory=cls.subcategory,
            weight_unit_measure_code='KG',
            size_unit_measure_code='CM',
            english_product_name='Laptop',
            standard_cost=1200.00,
            finished_goods_flag=True,
            color='Black',
            safety_stock_level=100,
            reorder_point=10,
            list_price=1500.00,
            days_to_manufacture=3,
            english_description='High-performance laptop',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=365),
            status='Active'
        )

    def test_product_creation(self):
        product = Product.objects.get(id=1)
        self.assertEqual(product.english_product_name, 'Laptop')
        self.assertEqual(product.product_subcategory, self.subcategory)
        self.assertTrue(product.finished_goods_flag)
        self.assertEqual(product.color, 'Black')
        self.assertEqual(product.status, 'Active')

    def test_product_string_representation(self):
        product = Product.objects.get(id=1)
        self.assertEqual(str(product), 'Laptop')

class ProductSubcategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Creating a product subcategory instance
        ProductSubcategory.objects.create(
            english_product_subcategory_name="Electronics",
            spanish_product_subcategory_name="Electrónica",
            french_product_subcategory_name="Électronique"
        )

    def test_subcategory_creation(self):
        subcategory = ProductSubcategory.objects.get(id=1)
        self.assertEqual(subcategory.english_product_subcategory_name, 'Electronics')
        self.assertEqual(subcategory.spanish_product_subcategory_name, 'Electrónica')
        self.assertEqual(subcategory.french_product_subcategory_name, 'Électronique')

    def test_subcategory_string_representation(self):
        subcategory = ProductSubcategory.objects.get(id=1)
        self.assertEqual(str(subcategory), 'Electronics')
