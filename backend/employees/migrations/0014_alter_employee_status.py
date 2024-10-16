# Generated by Django 5.0.6 on 2024-08-27 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0013_employee_date_meeting_employee_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=models.CharField(choices=[('onboarding', 'Онбординг'), ('offboarding', 'Оффбординг'), ('adapted', 'Адаптированный'), ('fired', 'Уволен'), ('riskzone', 'В зоне риска'), ('observable', 'Наблюдаемый')], default='onboarding', max_length=20, verbose_name='Статус сотрудника'),
        ),
    ]
