from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DeleteView

from .models import Order, Item
from .forms import OrderForm, ItemForm

# Create your views here.
class OrdersView(ListView):
    template_name = "orders/index.html"

    def get_queryset(self):
        return Order.objects.prefetch_related('item_set').all()


class OrderDetailsView(ListView):
    template_name = 'orders/order_details.html'

    def get_queryset(self):
        order = Order.objects.prefetch_related('item_set').get(pk=self.kwargs['pk'])
        if order is None:
            raise PermissionDenied()
        return Order.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        order = Order.objects.get(pk=self.kwargs["pk"])
        context["order"] = order
        return context


class OrderCreateView(View):
    ItemFormSet = modelformset_factory(Item, form=ItemForm)

    def get(self, request, *args, **kwargs):
        order_form = OrderForm()
        item_formset = self.ItemFormSet(queryset=Item.objects.none())
        return render(request, 'orders/create_order.html', {
            'order_form': order_form,
            'item_formset': item_formset
        })

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = self.ItemFormSet(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.status = 'в ожидании'
            order.save()

            if item_formset.is_valid():
                total_price = 0
                for item_form in item_formset:
                    item = item_form.save(commit=False)
                    if item:
                        total_price += item.price
                        item.order = order
                        item.save()

                order.total_price = total_price
                order.save()
                return redirect('index')

        return render(request, 'orders/create_order.html', {
            'order_form': order_form,
            'item_formset': item_formset
        })


class OrderUpdateView(View):
    ItemFormSet = modelformset_factory(Item, form=ItemForm, extra=0)

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        order_form = OrderForm(instance=order)
        item_formset = self.ItemFormSet(queryset=Item.objects.filter(order=order))
        return render(request, 'orders/update_order.html', {
            'order_form': order_form,
            'item_formset': item_formset,
            'order': order
        })

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        order_form = OrderForm(request.POST, instance=order)
        item_formset = self.ItemFormSet(request.POST, queryset=Item.objects.filter(order=order))

        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save()
            total_price = 0
            for item_form in item_formset:
                item = item_form.save(commit=False)
                if item:
                    total_price += item.price
                    item.order = order
                    item.save()

            order.total_price = total_price
            order.save()
            return redirect('index')

        return render(request, 'orders/update_order.html', {
            'order_form': order_form,
            'item_formset': item_formset,
            'order': order
        })


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return Order.objects.prefetch_related('item_set').all()

