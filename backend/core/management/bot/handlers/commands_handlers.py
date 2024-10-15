from datetime import date

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from core.management.bot.create_bot import bot
from core.management.bot.keyboards import registration_keyboard, main_keyboard, generate_list_polls_keyboard
from core.management.bot.states import ProcessHelp
from core.management.bot.utils.functions import get_employee, update_telegram_nickname, check_verification_code, \
    get_curator_for_employee, get_book
from core.management.bot.texts import texts_start_not_registered, texts_start_is_registered, texts_for_curator, \
    texts_reg_success_code, texts_reg_success_code_curator
from employees.models import Employee

router = Router(name='commands-router')


@router.message(CommandStart())
async def cmd_start_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /start
    Позволяет автоматически пройти регистрацию без доп действий если был передан аргумент с токеном в команде
    """
    current_state = await state.get_state()
    if current_state is None:
        employee = await get_employee(message.from_user.id)
        if not employee:
            try:
                _, code = message.text.split()
                registration = await check_verification_code(message.from_user.id, code)
                answer, employee = registration
                if not answer:
                    await message.answer(texts_start_not_registered, parse_mode='HTML',
                                         reply_markup=registration_keyboard())
                    return
                if employee.role == Employee.RoleChoices.EMPLOYEE:
                    book_employee = get_book('core/management/bot/files/book_employee.pdf')
                    curator = await get_curator_for_employee(employee)
                    curator_full_name = curator.full_name if curator else 'Не назначен'
                    await bot.send_document(message.from_user.id,
                                            caption=texts_reg_success_code.format(curator_full_name),
                                            document=book_employee, parse_mode='HTML',
                                            reply_markup=ReplyKeyboardRemove())
                else:
                    await bot.send_message(message.from_user.id, text=texts_reg_success_code_curator,
                                           parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
            except ValueError:
                await message.answer(texts_start_not_registered, parse_mode='HTML', reply_markup=registration_keyboard())
        else:
            await update_telegram_nickname(employee, message.from_user.username)
            if employee.role == Employee.RoleChoices.EMPLOYEE:
                await message.answer(texts_start_is_registered.format(f"@{message.from_user.username}"), parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
            elif employee.role == Employee.RoleChoices.CURATOR:
                await message.answer(texts_for_curator, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())

    else:
        await message.answer('Необходимо сначала закончить предыдущее действие или опрос')


@router.message(Command('help'))
async def cmd_help_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /help
    """
    current_state = await state.get_state()
    if current_state is None:
        employee = await get_employee(message.from_user.id)
        if not employee:
            await message.answer(texts_start_not_registered, parse_mode='HTML', reply_markup=registration_keyboard())
        else:
            await state.set_state(ProcessHelp.help)
            await message.answer('Расскажи о своей проблеме, и мы свяжемся с тобой в ближайшее время', reply_markup=main_keyboard(only_cancel=True))
    else:
        await message.answer('Необходимо сначала закончить предыдущее действие или опрос')


@router.message(Command('polls'))
async def check_polls_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        employee = await get_employee(message.from_user.id)
        if not employee:
            await message.answer(texts_start_not_registered, parse_mode='HTML', reply_markup=registration_keyboard())
        else:
            list_polls_keyboard = await generate_list_polls_keyboard(message.from_user.id)
            if list_polls_keyboard:
                await message.answer('Ваши непройденные опросы 👇', reply_markup=list_polls_keyboard)
            else:
                await message.answer('На данный момент все опросы пройдены')
    else:
        await message.answer('Необходимо сначала закончить предыдущее действие или опрос')