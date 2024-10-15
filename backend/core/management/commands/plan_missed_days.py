from datetime import datetime

from django.core.management.base import BaseCommand
from questions.tasks import schedule_create_pollstatuses


class Command(BaseCommand):
    help = ('Команда которая позволяет встроить в график те опросы, которые по любым причинам не встроились сами ('
            'например лежал планировщик)')

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            nargs='+',
            type=str,
            help='Список дней для которых запланировать создание опросов в YYYY-MM-DD формате'
        )

    def handle(self, *args, **options):
        days = options['days']

        if days:
            try:
                list_days = [datetime.strptime(day, '%Y-%m-%d').date() for day in days]
                schedule_create_pollstatuses.delay(list_days)
                self.stdout.write(self.style.SUCCESS(f'Создание опросов запланировано для {days} дней'))
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Ошибка парсинга дат: {e}'))
        else:
            schedule_create_pollstatuses.delay()
            self.stdout.write(self.style.SUCCESS('Создание опросов запланировано для вчерашнего и сегодняшнего дня'))