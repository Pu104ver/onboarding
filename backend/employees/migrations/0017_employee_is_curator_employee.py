# Generated by Django 5.0.6 on 2024-09-02 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0016_alter_curatoremployees_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_curator_employee',
            field=models.BooleanField(default=False, verbose_name='Куратор-сотрудник'),
        ),
    ]
