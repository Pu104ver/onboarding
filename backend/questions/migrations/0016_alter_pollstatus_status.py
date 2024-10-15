# Generated by Django 5.0.6 on 2024-08-16 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0015_alter_pollquestion_poll_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollstatus',
            name='status',
            field=models.CharField(choices=[('not_started', 'Не начат'), ('in_progress', 'В процессе'), ('in_frozen', 'Заморожен'), ('expired', 'Просрочен'), ('completed', 'Завершен')], default='not_started', max_length=20, verbose_name='Статус'),
        ),
    ]
