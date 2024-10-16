# Generated by Django 5.0.6 on 2024-07-23 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_employee_telegram_user_id_and_more'),
        ('questions', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pollstatus',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='feedbackuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='answered_by',
        ),
        migrations.AddField(
            model_name='feedbackuser',
            name='employee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='employees.employee', verbose_name='Пользователь'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pollstatus',
            name='target_employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target_employee_pollstatus', to='employees.employee', verbose_name='Сотрудник по которому происходит опрос'),
        ),
        migrations.AddField(
            model_name='useranswer',
            name='target_employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target_employee_useranswer', to='employees.employee', verbose_name='Сотрудник, по которому был дан ответ'),
        ),
        migrations.AlterField(
            model_name='pollstatus',
            name='employee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='employee_pollstatus', to='employees.employee', verbose_name='Сотрудник'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='useranswer',
            name='employee',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='employee_useranswer', to='employees.employee', verbose_name='Сотрудник'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='pollstatus',
            name='user',
        ),
    ]
