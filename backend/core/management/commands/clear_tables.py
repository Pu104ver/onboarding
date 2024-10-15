from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    # При последнем использовании команды для очискти таблиц приложения "questiions" - удалились еще и сотрудники, хоть сигналов на такое поведение я не обнаружил
    help = "Очистка всех таблиц указанного приложения или конкретных таблиц"

    def add_arguments(self, parser):
        parser.add_argument(
            "tables",
            nargs="+",
            type=str,
            help="Список таблиц для очистки в формате app_name или app_name.ModelName.",
        )

    def handle(self, *args, **options):
        tables = options["tables"]
        tables_to_truncate = []

        if (
            len(tables) == 1 and "." not in tables[0]
        ):  # Если указано только имя приложения
            app_label = tables[0]
            models = apps.get_app_config(app_label).get_models()
            for model in models:
                tables_to_truncate.append(model._meta.db_table)
        else:  # Если указаны конкретные таблицы
            for table in tables:
                try:
                    app_label, model_name = table.split(".")
                    model = apps.get_model(app_label, model_name)
                    tables_to_truncate.append(model._meta.db_table)
                except ValueError:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Ошибка: неверный формат для '{table}'. Ожидается 'app_name.ModelName'."
                        )
                    )
                    return
                except LookupError:
                    self.stderr.write(
                        self.style.ERROR(f"Ошибка: модель '{table}' не найдена.")
                    )
                    return
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Ошибка при очистке таблицы '{table}': {str(e)}"
                        )
                    )
                    return

        data_list = ", ".join(tables_to_truncate)
        confirmation_message = f"Вы уверены, что хотите выполнить очистку? Будут очищены следующие данные: {data_list}"

        confirm = input(f"{confirmation_message} (y/n): ")
        if confirm.lower() not in ["д", "да", "y", "yes"]:
            self.stdout.write(self.style.WARNING("Очистка отменена."))
            return

        for table in tables_to_truncate:
            self.truncate_table(table)

        self.stdout.write(self.style.SUCCESS("Очистка таблиц завершена."))

    def truncate_table(self, table_name):
        """Очистка таблицы и сброс счетчика первичного ключа."""
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
        self.stdout.write(f"Таблица '{table_name}' успешно очищена.")
