# Generated by Django 5.0.6 on 2024-09-24 21:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0028_alter_pollquestion_options_alter_pollstatus_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyboardtype',
            name='question_type',
            field=models.CharField(choices=[('yes_no', 'Yes/No'), ('finish', 'Finish'), ('message', 'Message'), ('next', 'Next'), ('numbers', 'Numbers'), ('slots', 'Slots')], max_length=50, unique=True, verbose_name='Тип вопроса'),
        ),
        migrations.AlterField(
            model_name='pollquestion',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название опроса'),
        ),
        migrations.AlterField(
            model_name='pollstatus',
            name='date_planned_at',
            field=models.DateField(blank=True, null=True, verbose_name='Дата уведомления'),
        ),
        migrations.AlterField(
            model_name='pollstatus',
            name='time_planned_at',
            field=models.CharField(blank=True, choices=[('morning', 'Утро'), ('evening', 'Вечер')], null=True, verbose_name='Время суток уведомления'),
        ),
        migrations.AlterField(
            model_name='question',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='questions.pollquestion', verbose_name='Опрос'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('yes_no', 'Yes/No'), ('finish', 'Finish'), ('message', 'Message'), ('next', 'Next'), ('numbers', 'Numbers'), ('slots', 'Slots')], max_length=50, verbose_name='Тип вопроса'),
        ),
        migrations.AlterField(
            model_name='question',
            name='show',
            field=models.BooleanField(default=True, verbose_name='Показывать вопрос'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(max_length=1024, verbose_name='Текст вопроса'),
        ),
        migrations.AlterField(
            model_name='questioncondition',
            name='answer_condition',
            field=models.CharField(choices=[('yes', 'Да'), ('no', 'Нет'), ('some_text', 'Некоторый текст'), ('next', 'Следующий'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=255, verbose_name='Условие'),
        ),
        migrations.AlterField(
            model_name='questioncondition',
            name='previous_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='previous_conditions', to='questions.question', verbose_name='Предыдущий вопрос'),
        ),
        migrations.AlterField(
            model_name='questioncondition',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='questions.question', verbose_name='Вопрос'),
        ),
    ]
