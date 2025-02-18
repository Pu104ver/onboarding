# Generated by Django 5.0.6 on 2024-08-16 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0011_alter_employee_telegram_nickname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='projects',
        ),
        migrations.AlterField(
            model_name='curatoremployees',
            name='curator',
            field=models.ForeignKey(limit_choices_to={'role': 'curator'}, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='employees.employee', verbose_name='Куратор'),
        ),
    ]
