# Generated by Django 5.0.6 on 2024-08-14 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0011_alter_employee_telegram_nickname'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Удален')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Время удаления')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('text', models.TextField(verbose_name='Описание проблемы')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee', verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
