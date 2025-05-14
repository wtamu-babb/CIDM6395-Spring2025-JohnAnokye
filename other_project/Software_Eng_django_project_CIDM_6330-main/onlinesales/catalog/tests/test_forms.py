from django.test import TestCase
from catalog.forms import OrderForm, CustomerRegistrationForm, OrderStatusForm
from catalog.models import Product, Orders, Customer, Currency
from django.contrib.auth.models import User
import datetime

class OrderFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.currency = Currency.objects.create(currency_alternate_key='USD', currency_name='United States Dollar')
        cls.product = Product.objects.create(english_product_name='Test Product', list_price=100.00, finished_goods_flag=True)
        cls.customer = Customer.objects.create(first_name='John', last_name='Doe', birth_date=datetime.date.today(), email_address='john@example.com')

    def test_form_fields(self):
        form = OrderForm()
        self.assertTrue('product' in form.fields)
        self.assertTrue('order_quantity' in form.fields)
        self.assertTrue('unit_price' in form.fields)
        self.assertTrue('extended_amount' in form.fields)
        self.assertTrue('currency' in form.fields)
        self.assertTrue('customer' in form.fields)
        self.assertEqual(form.fields['unit_price'].widget.attrs['readonly'], True)
        self.assertEqual(form.fields['extended_amount'].widget.attrs['readonly'], True)

    def test_form_save(self):
        form_data = {
            'product': self.product.id,
            'order_quantity': 10,
            'unit_price': 100.00,
            'currency': self.currency.id,
            'customer': self.customer.id,
            'extended_amount': 1000.00
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        order = form.save()
        self.assertEqual(order.extended_amount, 1000.00)
        self.assertEqual(Orders.objects.count(), 1)

class CustomerRegistrationFormTest(TestCase):
    def test_form_fields(self):
        form = CustomerRegistrationForm()
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birth_date']
        for field in fields:
            self.assertTrue(field in form.fields)

    def test_form_save(self):
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'birth_date': '1990-01-01'
        }
        form = CustomerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.get(user=user)
        self.assertEqual(customer.birth_date, datetime.date(1990, 1, 1))

class OrderStatusFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create user and customer
        user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        cls.customer = Customer.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            email_address='john@example.com',
            birth_date='1980-01-01'
        )

        # Create necessary Currency
        cls.currency = Currency.objects.create(
            currency_alternate_key='USD',
            currency_name='United States Dollar'
        )

        # Create a product
        cls.product = Product.objects.create(
            english_product_name='Example Product',
            list_price=150.00,
            finished_goods_flag=True,
            size_unit_measure_code='CM',
            weight_unit_measure_code='KG'
        )

        # Create an order with all required fields
        cls.order = Orders.objects.create(
            customer=cls.customer,
            product=cls.product,
            order_quantity=10,
            unit_price=150.00,
            currency=cls.currency
        )

    def test_form_init(self):
        form = OrderStatusForm(instance=self.order)
        self.assertEqual(form.instance, self.order)

    def test_form_save(self):
        form = OrderStatusForm({'status': 's'}, instance=self.order)
        self.assertTrue(form.is_valid())
        order = form.save()
        self.assertEqual(order.status, 's')
