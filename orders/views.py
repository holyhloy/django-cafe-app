from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, View, DeleteView
from rest_framework import viewsets

from .models import Order, Item
from .forms import OrderForm, ItemForm, OrderSearchForm, OrderEditForm
from .serializers import OrderCreateSerializer, OrderRetrieveSerializer, ItemSerializer


class OrdersView(ListView):
    template_name = "orders/index.html"

    def get_queryset(self):
        """Функция получает набор данных для отображения.
        Она получается объекты моделей Order, а также Item
        с помощью метода prefetch_related.
        Встроена фильтрация заказов по статусу"""

        status_filter = self.request.GET.get('status', 'all')

        if status_filter == 'all' or not status_filter:
            return Order.objects.prefetch_related('items').all()
        else:
            return Order.objects.prefetch_related('items').filter(status=status_filter)


class OrderDetailsView(ListView):
    template_name = 'orders/order_details.html'

    def get_queryset(self):
        """Функция получает набор данных для отображения.
        Она получает объекты моделей Order, а также Item
        с помощью метода prefetch_related.
        Встроена фильтрация заказов по статусу"""
        order = Order.objects.prefetch_related('items').get(pk=self.kwargs['pk'])
        if order is None:
            raise PermissionDenied()
        return Order.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        """Добавляет дополнительные данные в контекст шаблона.
        В данном случае объект заказа добавляется в контекст,
        чтобы его можно было использовать в шаблоне."""
        context = super().get_context_data(object_list=object_list, **kwargs)
        order = Order.objects.get(pk=self.kwargs["pk"])
        context["order"] = order
        return context


class OrderCreateView(View):
    ItemFormSet = modelformset_factory(Item, form=ItemForm)

    def get(self, request, *args, **kwargs):
        """Функция для отображения формы создания заказа
        и formset создания блюда при выполнении запроса GET"""
        order_form = OrderForm()
        item_formset = self.ItemFormSet(queryset=Item.objects.none())
        return render(request, 'orders/create_order.html', {
            'order_form': order_form,
            'item_formset': item_formset
        })

    def post(self, request, *args, **kwargs):
        """Функция для обработки формы создания заказа
        и formset создания блюда для выполнения запроса POST"""
        order_form = OrderForm(request.POST)
        item_formset = self.ItemFormSet(request.POST)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.status = 'в ожидании'
            order.save()

            if item_formset.is_valid():
                total_price = 0 # Переменная для расчета общей стоимости заказа
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

    ItemFormSet = modelformset_factory(Item, form=ItemForm, extra=1)

    def get(self, request, order_id, *args, **kwargs):
        """Функция для отображения формы редактирования заказа
        и formset создания блюда при выполнении запроса GET"""

        order = get_object_or_404(Order, id=order_id)
        order_form = OrderEditForm(instance=order)
        item_formset = self.ItemFormSet(queryset=Item.objects.filter(order=order))

        return render(request, 'orders/update_order.html', {
            'order_form': order_form,
            'item_formset': item_formset,
            'order': order
        })

    def post(self, request, order_id, *args, **kwargs):
        """Функция для обработки формы редактирования заказа
        и formset создания блюда для выполнения запроса POST.
        Переадресует на главную страницу при успешном выполнении"""
        order = get_object_or_404(Order, id=order_id)
        order_form = OrderEditForm(request.POST, instance=order)
        item_formset = self.ItemFormSet(request.POST, queryset=Item.objects.filter(order=order))

        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save()
            total_price = 0 # Переменная для расчета новой общей стоимости заказа
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
        """Функция получает набор данных для отображения
        и последующего удаления. Она возвращает объекты моделей
        Order, а также Item с помощью метода prefetch_related."""

        return Order.objects.prefetch_related('items').all()


class ItemDeleteView(DeleteView):
    model = Item

    def get_success_url(self):
        """Функция определяет url для перехода в случае успешного удаления"""
        order_id = self.object.order.id
        return reverse('update_order', args=[order_id])

    def get_queryset(self):
        """Функция получает набор данных для отображения
        и последующего удаления. Она возвращает объекты моделей
        Order, а также Item с помощью метода prefetch_related."""
        items = Item.objects.all()
        return items


class OrderSearchView(View):
    template_name = 'orders/search_orders.html'

    def get(self, request):
        """Функция получает из формы id и status заказа,
        а затем на их основе фильтрует данные, полученные из модели Order"""
        form = OrderSearchForm(request.GET or None)
        results = []

        if form.is_valid():
            order_id = form.cleaned_data.get('id')
            status = form.cleaned_data.get('status')

            filters = {}
            if order_id:
                filters['id'] = order_id
            if status:
                filters['status'] = status

            results = Order.objects.filter(**filters)

        return render(request, self.template_name, {'form': form, 'results': results})


class RevenueView(View):
    template_name = 'orders/revenue.html'

    def get_total_revenue(self):
        """Функция вычисляет общую выручку, основываясь на данных
        об общей стоимости заказов из модели Order"""
        total_revenue = Order.objects.aggregate(total=Sum('total_price'))
        return total_revenue['total'] if total_revenue['total'] else 0

    def get_amount_of_orders(self):
        """Функция считает количество заказов,
        основываясь на данных из модели Order"""
        amount_of_orders = Order.objects.aggregate(amount=Count('id'))
        return amount_of_orders['amount'] if amount_of_orders['amount'] else 0

    def get_average_bill(self):
        """Функция вычисляет средний чек, основываясь на данных
        об общей стоимости заказов из модели Order"""
        average_bill = Order.objects.aggregate(avg=Avg('total_price', default=0))
        return average_bill['avg'] if average_bill['avg'] else 0

    def get(self, request, *args, **kwargs):
        """Функция обновляет контекст, добавляя в него
        переменные total_revenue, amount_of_orders и average_bill,
        и затем передает их в шаблон класса"""
        total_revenue = self.get_total_revenue()
        amount_of_orders = self.get_amount_of_orders()
        average_bill = round(self.get_average_bill(), 2)
        context = {
            'total_revenue': total_revenue,
            'amount_of_orders': amount_of_orders,
            'average_bill': average_bill,
        }
        return render(request, self.template_name, context)


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.prefetch_related('items').all()

    def get_serializer_class(self):
        """Функция получает метод из запроса и
        возвращает Serializer для создания или
        отображения заказов"""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return OrderCreateSerializer
        return OrderRetrieveSerializer
