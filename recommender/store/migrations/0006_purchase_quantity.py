# Generated by Django 5.0.2 on 2025-04-19 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_purchase_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
