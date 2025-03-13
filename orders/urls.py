from django.urls import path

from .views import OrdersView, OrderDetailsView, OrderCreateView, OrderDeleteView, OrderUpdateView, OrderSearchView, \
    RevenueView, ItemDeleteView

urlpatterns = [
path('', OrdersView.as_view(), name='index'),
path('order/<int:pk>', OrderDetailsView.as_view(), name='order_details'),
path('order/create/', OrderCreateView.as_view(), name='create_order'),
path('order/<int:order_id>/update', OrderUpdateView.as_view(), name='update_order'),
path('order/<int:pk>/delete', OrderDeleteView.as_view(), name='delete_order'),
path('order/item/<int:pk>/delete', ItemDeleteView.as_view(), name='delete_item'),
path('search/', OrderSearchView.as_view(), name='search_orders'),
path('revenue/', RevenueView.as_view(), name='revenue'),
]