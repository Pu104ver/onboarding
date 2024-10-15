# Generated by Django 5.0.6 on 2024-08-22 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0018_useranswer_requires_attention'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollstatus',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время удаления'),
        ),
        migrations.AddField(
            model_name='pollstatus',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удален'),
        ),
    ]
