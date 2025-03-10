from django import forms
from .models import Order, Item


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number', 'status']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item', 'price']