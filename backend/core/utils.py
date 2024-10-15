import asyncio

from core.management.bot.create_bot import bot
from django.db import models
from django.db.models import Q
from typing import Optional


async def send_message_to_admins(admins, message):
    """
    Запускает асинхронную рассылку по админам
    """
    tasks = []
    for admin_id in admins:
        task = bot.send_message(chat_id=admin_id, text=message, parse_mode="HTML")
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


def check_object_existence(
    model: models.Model,
    ids: Optional[list[int]] = None,
    exist: bool = True,
    **filters,
) -> tuple[bool, Optional[str]]:
    """
    Проверяет существование объектов указанной модели с заданными идентификаторами и фильтрами.

    По сути своей является тестестероновым аналогом 'Model.objects.filter(pk__in=ids).exists()'.
    Функция создавалась, чтобы чуть сократить код в сервисах сотрудников, не переписывая 6 раз почти один и тот же код. В целом можно обойтись и без этой функции, но с ней, на момент ее написания мне казалось, удобнее.

    Args:
        model (django.db.models.Model): Модель объектов для проверки.
        ids (list, optional): Список идентификаторов для проверки. Если не указан, проверяет только фильтры.
        exist (bool): Если True, проверяет существование объектов; если False, проверяет их отсутствие.
        **filters: Дополнительные аргументы для фильтрации объектов по полям модели.
    Returns:
        tuple[bool, Optional[str]]: Кортеж, где первый элемент - булево значение, указывающее на результат проверки, второй элемент - ошибка (если есть).
    """

    query = Q()
    # заполняем запрос
    if ids:
        query &= Q(id__in=ids)
    for field, value in filters.items():
        query &= Q(**{field: value})

    existing_objects = model.objects.filter(query)
    existing_ids = list(existing_objects.values_list("id", flat=True))

    if ids:
        missing_ids = set(ids) - set(existing_ids)
    else:
        missing_ids = []

    error_message = f"Некоторые объекты {model.__name__} не существуют"
    error_message += f" или не соответствуют фильтрам {filters}." if filters else "."

    # Если проверка на существование не прошла
    if missing_ids and exist:
        return False, error_message

    # Если проверка на отсутствие не прошла
    elif existing_ids and not exist:
        return False, error_message
    
    return True, None
