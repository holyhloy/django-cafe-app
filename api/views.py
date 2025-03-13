from rest_framework import viewsets

from api.serializers import OrderCreateSerializer, OrderRetrieveSerializer
from orders.models import Order


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.prefetch_related('items').all()

    def get_serializer_class(self):
        """Функция получает метод из запроса и
        возвращает Serializer для создания или
        отображения заказов"""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return OrderCreateSerializer
        return OrderRetrieveSerializer
