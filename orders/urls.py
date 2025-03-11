from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrdersView, OrderDetailsView, OrderCreateView, OrderDeleteView, OrderUpdateView, OrderSearchView, \
    RevenueView, OrderViewSet, ItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
path('api/', include(router.urls)),
path('', OrdersView.as_view(), name='index'),
path('order/<int:pk>', OrderDetailsView.as_view(), name='order_details'),
path('create_order/', OrderCreateView.as_view(), name='create_order'),
path('order/<int:order_id>/update', OrderUpdateView.as_view(), name='update_order'),
path('order/<int:pk>/delete', OrderDeleteView.as_view(), name='delete_order'),
path('search/', OrderSearchView.as_view(), name='search_orders'),
path('revenue/', RevenueView.as_view(), name='revenue'),
]