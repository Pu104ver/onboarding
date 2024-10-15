import asyncio
from typing import List

from celery import shared_task

from core.utils import send_message_to_admins


@shared_task
def notification_admins(admins: List[int], message: str):
    """
    Celery-функция которая ставит задачу для рассылки по админам
    """
    if admins:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_message_to_admins(admins, message))
