from django import forms
from .models import Orders, Product, Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['product', 'order_quantity', 'unit_price', 'extended_amount','currency', 'customer']
        widgets = {
            #'order_date_actual': forms.DateInput(attrs={'type': 'date'}),
            #'due_date_actual': forms.DateInput(attrs={'type': 'date'}),
            #'ship_date_actual': forms.DateInput(attrs={'type': 'date'}),
            'unit_price': forms.TextInput(attrs={'readonly': True}),
            'extended_amount': forms.TextInput(attrs={'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        
        self.fields['product'].queryset = Product.objects.all()
        self.fields['product'].label_from_instance = lambda obj: f"{obj.english_product_name} (ID: {obj.id})"

        self.fields['product'].help_text = "Select a product by its ID and name"

    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=False)
        # IF 'unit_price' and 'order_quantity' are already validated as numbers:
        instance.extended_amount = instance.order_quantity * instance.unit_price
        if commit:
            instance.save()
        return instance
    
#class CustomerRegistrationForm(forms.ModelForm):
#    class Meta:
#        model = Customer
#        fields = ['first_name', 'last_name', 'birth_date', 'email_address']

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    birth_date = forms.DateField(required=True, help_text="Format: YYYY-MM-DD")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birth_date')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            customer = Customer.objects.create(
                user=user,
                birth_date=self.cleaned_data['birth_date'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email_address=self.cleaned_data['email']
            )
        return user
    
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(OrderStatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = "Update Order Status"