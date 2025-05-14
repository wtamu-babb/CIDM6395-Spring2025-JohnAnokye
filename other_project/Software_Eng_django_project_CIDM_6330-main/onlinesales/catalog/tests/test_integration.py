from django.test import TestCase
from django.urls import reverse
from catalog.models import Product, Customer, Orders, Date, Currency
from django.contrib.auth.models import User
from django.utils import timezone

class CatalogIntegrationTests(TestCase):
    def setUp(self):
        self.setUpUsers()
        self.setUpProducts()
        self.setUpDates()
        self.setUpCurrency()
        self.setUpOrder()

    def setUpUsers(self):
        print("Creating user...")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        print("Creating customer...")
        self.customer = Customer.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            birth_date='1990-01-01',
            email_address='johndoe@example.com'
        )

    def setUpProducts(self):
        print("Creating product...")
        self.product = Product.objects.create(
            english_product_name='Chair',
            list_price=29.99,
            inventory_count=10,
            finished_goods_flag=True
        )

    def setUpDates(self):
        print("Handling date...")
        date_key = timezone.now().date()
        self.date, created = Date.objects.get_or_create(
            full_date_alternate_key=date_key,
            defaults={
                'day_number_of_week': timezone.now().weekday(),
                'english_day_name_of_week': timezone.now().strftime('%A'),
                'month_number_of_year': timezone.now().month,
                'calendar_year': timezone.now().year,
                'day_number_of_month': timezone.now().day,
                'day_number_of_year': timezone.now().day,
                'calendar_quarter': 1,
                'week_number_of_year': timezone.now().isocalendar()[1]
            }
        )

    def setUpCurrency(self):
        print("Creating currency...")
        self.currency = Currency.objects.create(
            currency_alternate_key='USD',
            currency_name='United States Dollar'
        )

    def setUpOrder(self):
        print("Creating order...")
        self.order = Orders(
            product=self.product,
            customer=self.customer,
            order_date_actual=self.date,
            due_date_actual=self.date,
            ship_date_actual=self.date,
            currency=self.currency,
            order_quantity=1,
            unit_price=29.99,
            sales_order_number='001',
            status='p'
        )
        self.order.save()

    def test_product_list_view(self):
        print("Testing product list view...")
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chair')

    def test_order_creation(self):
        print("Testing order creation...")
        response = self.client.post(reverse('create-order'), {
            'product': self.product.id,
            'order_quantity': 1,
            'unit_price': self.product.list_price,
            'customer': self.customer.id
        })
        # Refresh the product to see if the inventory count has been updated
        self.product.refresh_from_db()
        self.assertEqual(self.product.inventory_count, 9)  
        self.assertEqual(response.status_code, 200)  

    def test_customer_detail_view(self):
        response = self.client.get(reverse('customer-detail', args=[self.user.customer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.customer.first_name)
        self.assertContains(response, self.user.customer.last_name)

    def test_product_detail_view(self):
        response = self.client.get(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.english_product_name)
        self.assertContains(response, self.product.list_price)

    def test_nonexistent_product_detail(self):
        response = self.client.get(reverse('product-detail', args=[999]))  # Assuming ID 999 does not exist
        self.assertEqual(response.status_code, 404)

