from typing import Tuple, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from core.management.bot.config import BOT_TOKEN


def initial_bot(token: str | None) -> Tuple[Optional[Bot], Optional[Dispatcher]]:
    """Инициализирует бота если найден токен в энвах"""
    if token:
        return Bot(token), Dispatcher()
    return None, None


bot, dp = initial_bot(BOT_TOKEN)

commands = [
    BotCommand(command='/start', description='Начать работу'),
    BotCommand(command='/help', description='Обратиться за помощью'),
    BotCommand(command='/polls', description='Проверить наличие опросов')
]


async def set_bot_commands():
    """Устанавливает команды для меню бота"""
    await bot.set_my_commands(commands)
