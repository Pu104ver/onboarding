from celery import shared_task
from django.utils import timezone

from slots.models import Slot


@shared_task
def schedule_recreate_slots():
    """
    Функция Celery, создающая слоты на день в 00:00 наступившего дня
    """
    today = timezone.now().date()
    Slot.objects.get_or_create(start_time='15:00', date=today)
    Slot.objects.get_or_create(start_time='16:00', date=today)
    Slot.objects.get_or_create(start_time='17:00', date=today)
    Slot.objects.get_or_create(start_time='18:00', date=today)
