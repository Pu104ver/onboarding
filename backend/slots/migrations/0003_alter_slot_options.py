# Generated by Django 5.0.6 on 2024-08-29 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0002_slot_deleted_at_slot_is_deleted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slot',
            options={'verbose_name': 'Слот', 'verbose_name_plural': 'Слоты'},
        ),
    ]
