# Generated by Django 5.0.6 on 2024-08-12 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0010_pollquestion_poll_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollquestion',
            name='intended_for',
            field=models.CharField(choices=[('employee', 'Сотрудник'), ('curator', 'Куратор')], default='employee', verbose_name='Предназначен для'),
        ),
    ]
