# Generated by Django 5.1.7 on 2025-03-10 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_item_model_edited'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('в ожидании', 'В ожидании'), ('готов', 'Готов'), ('оплачен', 'Оплачен')], default='В ожидании', max_length=100),
        ),
    ]
