# Generated by Django 5.0.6 on 2024-08-15 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0014_alter_pollquestion_content_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollquestion',
            name='poll_type',
            field=models.CharField(choices=[('onboarding', 'Онбординг'), ('offboarding', 'Офбординг'), ('feedback', 'Обратная связь')], default='onboarding', max_length=50, verbose_name='Тип опроса'),
        ),
    ]
