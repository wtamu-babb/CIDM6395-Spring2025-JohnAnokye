from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Orders, Customer, ProductSubcategory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import OrderForm
from django.http import HttpResponse
import json
from .forms import CustomerRegistrationForm
from .forms import OrderStatusForm

def index(request):
    """View function for the home page of the site."""
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    product_subcategories = ProductSubcategory.objects.annotate(total_products=Count('product'))
    
    context = {
        'product_subcategories': product_subcategories,
        'num_visits': num_visits,
    }

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email_address=request.user.email)
            shipped_orders = Orders.objects.filter(customer=customer, status='s').order_by('-order_date')[:5]
            context['shipped_orders'] = shipped_orders
        except Customer.DoesNotExist:
            context['shipped_orders'] = None
    # Checking if user is authenticated and has the 'catalog.can_mark_shipped' permission
    if request.user.is_authenticated and request.user.has_perm('catalog.can_mark_shipped'):
        shipped_orders = Orders.objects.filter(status='s').order_by('-order_date')
        context['shipped_orders'] = shipped_orders

    return render(request, 'catalog/index.html', context)


class ProductListView(ListView):
    model = Product
    paginate_by = 5  # Display 5 products per page
    template_name = 'catalog/product_list.html'
    context_object_name = 'product_list'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Get the number of visits to this view, as counted in the session variable
        num_visits = self.request.session.get('num_product_list_visits', 0)
        self.request.session['num_product_list_visits'] = num_visits + 1
        # Add number of visits to context
        context['num_visits'] = num_visits
        # Add in the product subcategories
        context['product_subcategories'] = ProductSubcategory.objects.annotate(total_products=Count('product'))
        return context

'''@login_required
def RecentOrdersView(request):
    """View function to display recent orders for the logged-in user."""
    recent_orders_list = Orders.objects.filter(customer__user=request.user).order_by('-order_date')[:10]

    context = {
        'recent_orders_list': recent_orders_list,
    }

    return render(request, 'catalog/recent_orders_list.html', context=context)'''

class RecentOrdersListView(LoginRequiredMixin, ListView):
    model = Orders
    template_name = 'catalog/recent_orders_list.html'
    context_object_name = 'recent_orders_list'
    paginate_by = 10  # Display 10 orders per page

    def get_queryset(self):
        # Ensure the user is authenticated and has an email
        if self.request.user.is_authenticated and self.request.user.email:
            user_email = self.request.user.email
            try:
                # Attempt to find a matching Customer based on the User's email
                customer = Customer.objects.get(email_address=user_email)
                # Filter orders by the retrieved customer and return them
                return Orders.objects.filter(customer=customer).order_by('-order_date')
            except ObjectDoesNotExist:
                # If no Customer matches, return an empty queryset
                return Orders.objects.none()
        else:
            # If the user is not authenticated or doesn't have an email, also return an empty queryset
            return Orders.objects.none()

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'catalog/customer_detail.html'

class ProductSubcategoryListView(ListView):
    model = ProductSubcategory
    template_name = 'catalog/product_subcategory_list.html'
    context_object_name = 'product_subcategories'

def product_subcategory_view(request, subcategory_id):
    """ display products by subcategory."""
    subcategory = get_object_or_404(ProductSubcategory, id=subcategory_id)
    products = Product.objects.filter(product_subcategory=subcategory)
    return render(request, 'catalog/product_list_by_subcategory.html', {'products': products, 'subcategory': subcategory})

class ShippedOrdersListView(LoginRequiredMixin, ListView):
    permission_required = 'catalog.can_mark_shipped'
    model = Orders
    template_name = 'catalog/shipping.html' 
    context_object_name = 'shipped_orders'

    def get_queryset(self):
        """Override to filter orders to those that have been shipped."""
        return Orders.objects.filter(status='s').order_by('-order_date')

class ShippedOrdersByUserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'catalog.can_mark_shipped'
    model = Orders
    template_name = 'catalog/shipped_orders_list_by_user.html'
    context_object_name = 'shipped_orders'

    def get_queryset(self):
        user_email = self.request.user.email
        try:
            # Attempt to find the Customer by email
            customer = Customer.objects.get(email_address=user_email)
            # Filter Orders by Customer
            return Orders.objects.filter(customer=customer, status='s').order_by('-order_date')
        except ObjectDoesNotExist:
            # If no matching Customer is found, return an empty queryset
            return Orders.objects.none()
        
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = OrderForm()

    products = Product.objects.all().values('id', 'list_price')
    product_prices = json.dumps({str(product['id']): (float(product['list_price']) if product['list_price'] else 0) for product in products})
    return render(request, 'catalog/order_form.html', {'form': form, 'product_prices': product_prices})


'''def register_customer(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirect logged-in users to home page
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = CustomerRegistrationForm()
    return render(request, 'catalog/register_customer.html', {'form': form})'''

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirect logged-in users to home page

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to login page after registration
        else:
            print(form.errors)

    else:
        form = CustomerRegistrationForm()

    return render(request, 'catalog/register_customer.html', {'form': form})


@permission_required('catalog.can_mark_shipped', raise_exception=True)
def update_order_status(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('all-orders')  # Redirect to  orders listing page
    else:
        form = OrderStatusForm(instance=order)

    return render(request, 'catalog/update_order_status.html', {'form': form, 'order': order})


class AllOrdersListView(PermissionRequiredMixin, ListView):
    model = Orders
    template_name = 'catalog/all_orders_list.html'
    context_object_name = 'orders'
    permission_required = 'catalog.can_mark_shipped'  # Ensuring only authorized users can view this

    def get_queryset(self):
        return Orders.objects.all().order_by('-order_date')  