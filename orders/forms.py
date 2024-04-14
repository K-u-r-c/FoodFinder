from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'city', 'pin_code']
        # widgets = {
        #     'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
        #     'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        #     'phone': forms.TextInput(attrs={'placeholder': 'Phone'}),
        #     'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        #     'address': forms.TextInput(attrs={'placeholder': 'Address'}),
        #     'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        #     'state': forms.TextInput(attrs={'placeholder': 'State'}),
        #     'city': forms.TextInput(attrs={'placeholder': 'City'}),
        #     'pin_code': forms.TextInput(attrs={'placeholder': 'Pin Code'}),
        # }
