# Generated by Django 5.0.6 on 2024-07-23 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('text', models.TextField(verbose_name='Описание проблемы')),
            ],
        ),
        migrations.CreateModel(
            name='KeyboardType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(choices=[('yes_no', 'Yes/No'), ('finish', 'Finish'), ('message', 'Message'), ('next', 'Next'), ('numbers', 'Numbers')], max_length=50, unique=True)),
                ('keyboard_json', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='PollQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField(default='Ответь на несколько вопросов', max_length=1024, verbose_name='Сообщение старта опроса')),
                ('days_after_hire', models.IntegerField(default=0, help_text='Количество дней после даты устройства сотрудника, когда должен начаться опрос', verbose_name='Дни после устройства')),
                ('time_of_day', models.CharField(choices=[('morning', 'Утро'), ('evening', 'Вечер')], default='morning', max_length=10, verbose_name='Время суток начала опроса')),
                ('intended_for', models.CharField(choices=[('EMPLOYEE', 'Сотрудник'), ('CURATOR', 'Куратор')], default='EMPLOYEE', verbose_name='Предназначен для')),
            ],
        ),
        migrations.CreateModel(
            name='PollStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Не начат'), ('in_progress', 'В процессе'), ('in_frozen', 'Заморожен'), ('completed', 'Завершен')], default='not_started', max_length=20, verbose_name='Статус')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время начала')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время завершения')),
                ('date_planned_at', models.DateField(blank=True, null=True, verbose_name='Дата, когда пользователь будет уведомлен')),
                ('time_planned_at', models.CharField(blank=True, choices=[('morning', 'Утро'), ('evening', 'Вечер')], null=True, verbose_name='Время, когда пользователь будет уведомлен')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1024)),
                ('question_type', models.CharField(choices=[('yes_no', 'Yes/No'), ('finish', 'Finish'), ('message', 'Message'), ('next', 'Next'), ('numbers', 'Numbers')], max_length=50)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='QuestionCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_condition', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('some_text', 'some_text'), ('next', 'Next'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(max_length=1024, verbose_name='Ответ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа')),
            ],
        ),
    ]
