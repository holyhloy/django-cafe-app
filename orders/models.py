from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Order(models.Model):
    STATUS_CHOICES = [
        ('в ожидании', 'В ожидании'),
        ('готов', 'Готов'),
        ('оплачен', 'Оплачен'),
    ]

    table_number = models.IntegerField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='В ожидании')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Заказ {self.pk}'


class Item(models.Model):
    item = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')