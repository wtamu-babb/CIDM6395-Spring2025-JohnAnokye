from django.contrib import admin
from .models import Orders, Customer, Date, Promotion, Currency, Product, ProductSubcategory

# Register your models here.
# Function to display shipping status in the admin list view
def order_status(obj):
    return obj.get_status_display()
order_status.short_description = 'Status'

class OrdersAdmin(admin.ModelAdmin):
    list_display = ('sales_order_number', 'customer', 'order_date_actual', 'sales_amount', order_status)
    list_filter = ('order_date_actual', 'ship_date_actual','customer', 'status')  # filtering by status
    search_fields = ('sales_order_number', 'customer__first_name', 'customer__last_name')

admin.site.register(Orders, OrdersAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_address', 'phone')
    search_fields = ('first_name', 'last_name', 'email_address')

admin.site.register(Customer, CustomerAdmin)

class DateAdmin(admin.ModelAdmin):
    list_display = ('full_date_alternate_key', 'english_day_name_of_week', 'english_month_name', 'calendar_year')
    list_filter = ('calendar_year', 'english_month_name')
    search_fields = ('full_date_alternate_key', 'english_month_name', 'calendar_year')

admin.site.register(Date, DateAdmin)

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('english_promotion_name', 'start_date', 'end_date', 'discount_pct')
    list_filter = ('start_date', 'end_date')
    search_fields = ('english_promotion_name',)

admin.site.register(Promotion, PromotionAdmin)

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_name', 'currency_alternate_key')
    search_fields = ('currency_name', 'currency_alternate_key')

admin.site.register(Currency, CurrencyAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('english_product_name', 'product_subcategory', 'standard_cost', 'list_price')
    list_filter = ('product_subcategory', 'standard_cost')
    search_fields = ('english_product_name', 'product_subcategory__english_product_subcategory_name')

admin.site.register(Product, ProductAdmin)

class ProductSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('english_product_subcategory_name',)
    search_fields = ('english_product_subcategory_name',)

admin.site.register(ProductSubcategory, ProductSubcategoryAdmin)

