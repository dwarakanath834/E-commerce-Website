from django import forms

from .models import Order


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=24)
    street = forms.CharField(max_length=255, label="Delivery address")
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    payment_method = forms.ChoiceField(choices=Order.PaymentMethod.choices, widget=forms.RadioSelect)
    save_address = forms.BooleanField(required=False, initial=True)


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Order.Status.choices)