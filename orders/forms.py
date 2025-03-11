from random import choices

from django import forms
from .models import Order, Item


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number']


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item', 'price']


class OrderSearchForm(forms.Form):
    STATUS_CHOICES = [
        ('','пусто'),
        ('в ожидании', 'В ожидании'),
        ('готов', 'Готов'),
        ('оплачен', 'Оплачен'),
    ]

    id = forms.IntegerField(required=False, label='ID заказа')
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, label='Статус')