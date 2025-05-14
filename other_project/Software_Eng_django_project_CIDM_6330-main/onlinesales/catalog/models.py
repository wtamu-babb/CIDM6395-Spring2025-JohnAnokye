from django.db import models
from django.urls import reverse
from django.conf import settings
from datetime import date
import uuid
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Orders(models.Model):
    product = models.ForeignKey('Product', on_delete=models.RESTRICT, help_text="Select product for this sale")
    order_date = models.ForeignKey('Date', related_name='orders_order_date', on_delete=models.RESTRICT, help_text="Select order date", null=True, blank=True)
    due_date = models.ForeignKey('Date', related_name='orders_due_date', on_delete=models.RESTRICT, help_text="Select due date", null=True, blank=True)
    ship_date = models.ForeignKey('Date', related_name='orders_ship_date', on_delete=models.RESTRICT, help_text="Select ship date", null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.RESTRICT, help_text="Select customer for this sale")
    #promotion = models.ForeignKey('Promotion', on_delete=models.RESTRICT, help_text="Select promotion applied to this sale")
    currency = models.ForeignKey('Currency', on_delete=models.RESTRICT, help_text="Select currency for this sale")
    #sales_territory = models.ForeignKey('SalesTerritory', on_delete=models.RESTRICT, help_text="Select sales territory for this sale")
    sales_order_number = models.CharField(max_length=20, help_text="Enter sales order number", blank=True)
    sales_order_line_number = models.PositiveSmallIntegerField(help_text="Enter sales order line number", null=True, blank=True)
    revision_number = models.PositiveSmallIntegerField(help_text="Enter revision number",  null=True, blank=True)
    order_quantity = models.PositiveSmallIntegerField(help_text="Enter order quantity")
    unit_price = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter unit price")
    extended_amount = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter extended amount", null=True, blank=True)
    unit_price_discount_pct = models.FloatField(help_text="Enter unit price discount percent", null=True, blank=True)
    discount_amount = models.FloatField(help_text="Enter discount amount", null=True, blank=True)
    product_standard_cost = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter product standard cost", null=True, blank=True)
    total_product_cost = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter total product cost", null=True, blank=True)
    sales_amount = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter sales amount", null=True, blank=True)
    tax_amt = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter tax amount", null=True, blank=True)
    freight = models.DecimalField(max_digits=19, decimal_places=4, help_text="Enter freight", null=True, blank=True)
    order_date_actual = models.DateTimeField(null=True, blank=True, help_text="Enter the actual order date")
    due_date_actual = models.DateTimeField(null=True, blank=True, help_text="Enter the actual due date")
    ship_date_actual = models.DateTimeField(null=True, blank=True, help_text="Enter the actual ship date")
    promotions = models.ManyToManyField('Promotion', blank=True, help_text="Select promotions for this order")
    ORDER_STATUS = (
        ('p', 'Processing'),
        ('s', 'Shipped'),
        ('d', 'Delivered'),
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        blank=True,
        default='p',
        help_text='Order Status',
    )

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        unique_together = ('sales_order_number', 'sales_order_line_number')

    class Meta:
        permissions = (
            ("can_mark_shipped", "Can mark order as shipped"),
        )  

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.sales_order_number}-{self.sales_order_line_number}'

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this order."""
        return reverse('order-detail', args=[str(self.id)])

    #def save(self, *args, **kwargs):
        #if not self.sales_order_number:
            # Generate a unique identifier for the sales order number
            #self.sales_order_number = str(uuid.uuid4())[:8]  
        #super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.id:  # Dates are set only when the order is first created
            now = timezone.now()
            self.order_date_actual = now
            self.due_date_actual = now + timedelta(days=1)
            self.ship_date_actual = now + timedelta(days=2)

        if not self.sales_order_number:
            self.sales_order_number = str(uuid.uuid4())[:8]  # Generate unique order number if not set

        super().save(*args, **kwargs)
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=True)
    """Model representing a customer."""
    customer_alternate_key = models.CharField(max_length=15, unique=True, default=uuid.uuid4)
    title = models.CharField(max_length=8, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    birth_date = models.DateField(null=False, blank=False)
    gender = models.CharField(max_length=1, null=True, blank=True)
    email_address = models.CharField(max_length=50, null=False, blank=False)
    english_education = models.CharField(max_length=40, null=True, blank=True)
    spanish_education = models.CharField(max_length=40, null=True, blank=True)
    french_education = models.CharField(max_length=40, null=True, blank=True)
    english_occupation = models.CharField(max_length=100, null=True, blank=True)
    spanish_occupation = models.CharField(max_length=100, null=True, blank=True)
    french_occupation = models.CharField(max_length=100, null=True, blank=True)
    house_owner_flag = models.CharField(max_length=1, null=True, blank=True)
    number_cars_owned = models.PositiveSmallIntegerField(null=True, blank=True)
    address_line1 = models.CharField(max_length=120, null=True, blank=True)
    address_line2 = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    date_first_purchase = models.DateField(null=True, blank=True)
    commute_distance = models.CharField(max_length=15, null=True, blank=True)
    #geography = models.ForeignKey('Geography', on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this customer."""
        return reverse('customer-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.customer_alternate_key:
            self.customer_alternate_key = str(uuid.uuid4())[:15]  # Generating a unique key
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('customer-detail', args=[str(self.id)])


class Date(models.Model):
    """Model representing a date dimension."""
    date_key = models.IntegerField(primary_key=True)
    full_date_alternate_key = models.DateField()
    day_number_of_week = models.PositiveSmallIntegerField()
    english_day_name_of_week = models.CharField(max_length=10)
    spanish_day_name_of_week = models.CharField(max_length=10)
    french_day_name_of_week = models.CharField(max_length=10)
    day_number_of_month = models.PositiveSmallIntegerField()
    day_number_of_year = models.PositiveSmallIntegerField()
    week_number_of_year = models.PositiveSmallIntegerField()
    english_month_name = models.CharField(max_length=10)
    spanish_month_name = models.CharField(max_length=10)
    french_month_name = models.CharField(max_length=10)
    month_number_of_year = models.PositiveSmallIntegerField()
    calendar_quarter = models.PositiveSmallIntegerField()
    calendar_year = models.SmallIntegerField()
    calendar_semester = models.PositiveSmallIntegerField(null=True, blank=True)
    fiscal_quarter = models.PositiveSmallIntegerField(null=True, blank=True)
    fiscal_year = models.SmallIntegerField(null=True, blank=True)
    fiscal_semester = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Date'
        verbose_name_plural = 'Dates'

    def __str__(self):
        """String for representing the Model object."""
        return self.full_date_alternate_key.strftime('%Y-%m-%d')

class Promotion(models.Model):
    """Model representing a promotion."""
    promotion_alternate_key = models.IntegerField(unique=True, null=True, blank=True)
    english_promotion_name = models.CharField(max_length=255, null=True, blank=True)
    spanish_promotion_name = models.CharField(max_length=255, null=True, blank=True)
    french_promotion_name = models.CharField(max_length=255, null=True, blank=True)
    discount_pct = models.FloatField(null=True, blank=True)
    english_promotion_type = models.CharField(max_length=50, null=True, blank=True)
    spanish_promotion_type = models.CharField(max_length=50, null=True, blank=True)
    french_promotion_type = models.CharField(max_length=50, null=True, blank=True)
    english_promotion_category = models.CharField(max_length=50, null=True, blank=True)
    spanish_promotion_category = models.CharField(max_length=50, null=True, blank=True)
    french_promotion_category = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    min_qty = models.IntegerField(null=True, blank=True)
    max_qty = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'

    def __str__(self):
        """String for representing the Model object."""
        return self.english_promotion_name if self.english_promotion_name else 'Unnamed Promotion'


class Currency(models.Model):
    """Model representing a currency."""
    currency_alternate_key = models.CharField(max_length=3, unique=True, help_text="Enter the currency code (e.g., USD, EUR)")
    currency_name = models.CharField(max_length=50, help_text="Enter the currency name (e.g., United States Dollar, Euro)")

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.currency_name} ({self.currency_alternate_key})'

class Product(models.Model):
    """Model representing a product."""
    product_alternate_key = models.CharField(max_length=25, null=True, blank=True, unique=True, help_text="Enter the product alternate key")
    product_subcategory = models.ForeignKey('ProductSubcategory', on_delete=models.SET_NULL, null=True, blank=True, help_text="Select the product subcategory")
    weight_unit_measure_code = models.CharField(max_length=3, null=True, blank=True, help_text="Enter the weight unit measure code")
    size_unit_measure_code = models.CharField(max_length=3, null=True, blank=True, help_text="Enter the size unit measure code")
    english_product_name = models.CharField(max_length=50, help_text="Enter the English name of the product")
    standard_cost = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True, help_text="Enter the standard cost of the product")
    finished_goods_flag = models.BooleanField(help_text="Indicate whether the product is a finished good")
    color = models.CharField(max_length=15, help_text="Enter the color of the product")
    inventory_count = models.IntegerField(default=100, help_text="Inventory count of the product")
    safety_stock_level = models.SmallIntegerField(null=True, blank=True, help_text="Enter the safety stock level")
    reorder_point = models.SmallIntegerField(null=True, blank=True, help_text="Enter the reorder point")
    list_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True, help_text="Enter the list price of the product")
    days_to_manufacture = models.IntegerField(null=True, blank=True, help_text="Enter the number of days required to manufacture the product")
    english_description = models.TextField(max_length=400, null=True, blank=True, help_text="Enter the English description of the product")
    start_date = models.DateTimeField(null=True, blank=True, help_text="Enter the start date of the product availability")
    end_date = models.DateTimeField(null=True, blank=True, help_text="Enter the end date of the product availability")
    status = models.CharField(max_length=7, null=True, blank=True, help_text="Enter the status of the product")

    def __str__(self):
        return f"{self.english_product_name} (ID: {self.id})"

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        """String for representing the Model object."""
        return self.english_product_name

class ProductSubcategory(models.Model):
    """Model representing a product subcategory."""
    product_subcategory_alternate_key = models.IntegerField(null=True, blank=True, unique=True, help_text="Enter the product subcategory alternate key")
    english_product_subcategory_name = models.CharField(max_length=50, help_text="Enter the English name of the product subcategory")
    spanish_product_subcategory_name = models.CharField(max_length=50, null=True, blank=True, help_text="Enter the Spanish name of the product subcategory")
    french_product_subcategory_name = models.CharField(max_length=50, null=True, blank=True, help_text="Enter the French name of the product subcategory")

    class Meta:
        verbose_name = 'Product Subcategory'
        verbose_name_plural = 'Product Subcategories'

    def __str__(self):
        """String for representing the Model object."""
        return self.english_product_subcategory_name
