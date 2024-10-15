import asyncio
from datetime import datetime

from celery import shared_task
from django.utils import timezone

from employees.models import Employee
from employees.utils import send_message_to_employee_tg, send_message_to_curator_tg


@shared_task
def send_planned_meeting_notification(telegram_user_id, datetime_meeting, rescheduled):
    """Таска для сигнала установки даты встречи по итогам ИС, отправляет увед в бота"""
    datetime_meeting = datetime_meeting.isoformat()
    formatted_datetime = datetime.fromisoformat(datetime_meeting).strftime('%d.%m.%Y %H:%M')
    if rescheduled:
        message = f'Ваша встреча по итогам испытательного срока перенесена на {formatted_datetime}'
    else:
        message = f'Вам назначена встреча по итогам испытательного срока на {formatted_datetime}'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message_to_employee_tg(chat_id=telegram_user_id, message=message))


@shared_task
def send_notification_curator(telegram_user_id, message):
    """Таска для отправки памятки куратора в бота"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message_to_curator_tg(chat_id=telegram_user_id, message=message))


@shared_task
def update_status_employee():
    """Таска для обновления статуса сотрудника"""
    today = timezone.now().date()

    employees = Employee.objects.filter(date_meeting__date=today, status=Employee.EmployeeStatus.ONBOARDING)

    for employee in employees:
        employee.status = Employee.EmployeeStatus.ADAPTED
        employee.save()

    employees = Employee.objects.filter(date_of_dismission__date=today, status=Employee.EmployeeStatus.OFFBOARDING)

    for employee in employees:
        employee.status = Employee.EmployeeStatus.FIRED
        employee.is_archived = True
        employee.save()
