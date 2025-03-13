from django.template.context_processors import request
from rest_framework import serializers
from .models import Order, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item', 'price']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['table_number', 'status', 'items']

    def create(self, validated_data):
        """Функция для создания заказа в рамках API"""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_price = 0
        for item_data in items_data:
            item = Item.objects.create(order=order, **item_data)
            total_price += item.price

        order.total_price = total_price
        order.save()
        return order

    def update(self, instance, validated_data):
        """Функция для редактирования заказа в рамках API"""
        items_data = validated_data.pop('items', [])

        # Обновляем основные поля заказа
        instance.table_number = validated_data.get('table_number', instance.table_number)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Сохраняем идентификаторы существующих элементов для последующего удаления
        existing_item_ids = {item.id for item in instance.items.all()}

        # Обновляем или создаем элементы
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_item_ids:
                # Обновляем существующий элемент
                item = Item.objects.get(id=item_id, order=instance)
                item.item = item_data.get('item', item.item)
                item.price = item_data.get('price', item.price)
                item.save()
                existing_item_ids.remove(item_id)  # Удаляем из множества, так как этот элемент обновлен
            else:
                # Создаем новый элемент
                Item.objects.create(order=instance, **item_data)

        # Удаляем элементы, которые не были обновлены или созданы
        for item_id in existing_item_ids:
            Item.objects.filter(id=item_id, order=instance).delete()

        return instance


class OrderRetrieveSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'total_price', 'items']
