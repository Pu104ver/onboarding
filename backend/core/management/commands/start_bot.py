import asyncio

from django.core.management.base import BaseCommand

from core.management.bot.create_bot import bot, dp, set_bot_commands
from core.management.bot.handlers.commands_handlers import router as command_router
from core.management.bot.handlers.callbacks_handlers import router as callback_router
from core.management.bot.handlers.messages_handlers import router as message_router


async def start_bot():
    if not bot:
        raise Exception('Токен бота не задан')
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands()
    dp.include_router(command_router)
    dp.include_router(callback_router)
    dp.include_router(message_router)
    await dp.start_polling(bot)


class Command(BaseCommand):
    help = 'Телеграм бот'

    def handle(self, *args, **kwargs):
        asyncio.run(start_bot())

