from typing import List

from core.management.bot.create_bot import bot
from core.management.bot.utils.functions import get_book
from employees.models import Employee, CuratorEmployees
from projects.models import ProjectAssignment


async def send_message_to_employee_tg(chat_id: int | None, message: str):
    """
    Отправляет любое текстовое сообщение в бота
    """
    if chat_id:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
            )
        except Exception:
            pass


async def send_message_to_curator_tg(chat_id: int | None, message: str):
    """
    Отправляет памятку куратору в бота
    """
    if chat_id:
        try:
            await bot.send_document(
                chat_id,
                caption=message,
                document=get_book('core/management/bot/files/book_curator.pdf')
            )
        except Exception:
            pass


def get_curators_as_employees() -> List[Employee]:
    """
    Получаем всех кураторов которые работают как сотрудники
    """
    curators = Employee.objects.filter(
        role=Employee.RoleChoices.CURATOR,
        is_curator_employee=True
    )

    return list(curators)
