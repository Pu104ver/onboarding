import asyncio
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from core.management.bot.create_bot import bot
from core.management.bot.keyboards import generate_answers_keyboard, registration_keyboard
from core.management.bot.texts import texts_reg_success_code, texts_start_is_registered, texts_reg_invalid_code, \
    texts_start_not_registered, texts_reg_success_code_employee, texts_for_curator
from core.management.bot.utils.functions import get_next_question_id, get_question_for_id, \
    check_verification_code, save_user_answer, delete_user_answer, get_poll_status, completed_poll_status, \
    create_feedback_employee, get_employee, get_curator_for_employee, update_telegram_nickname, \
    send_notification_admins, get_book, cancel_poll_status
from core.management.bot.states import ProcessInterview, ProcessRegistration, ProcessHelp
from employees.models import Employee
from questions.models import PollStatus

router = Router(name='messages-router')


async def handler_question(message: Message, state: FSMContext, current_question, delete_message_id=None):
    """
    Функция обработки нового вопроса
    """
    keyboard = await generate_answers_keyboard(question_id=current_question.id, question_type=current_question.question_type)
    if delete_message_id:
        await message.delete()
        await bot.delete_message(message.from_user.id, delete_message_id)
    new_message = await message.answer(current_question.text, reply_markup=keyboard)
    if current_question.question_type == 'finish':
        data = await state.get_data()
        await completed_poll_status(poll_id=data['poll_id'],
                                    telegram_user_id=message.from_user.id,
                                    target_employee_id=data['target_employee_id'])
        await state.clear()
        await bot.delete_message(message.from_user.id, data['temp_message_id'])
    else:
        await state.update_data(message_id=new_message.message_id, question_id=current_question.id)


@router.message(F.text == 'Назад')
async def message_back_handler(message: Message, state: FSMContext):
    """
    Обработка клавиши назад
    """
    current_state = await state.get_state()
    if current_state == ProcessInterview.interview:
        data = await state.get_data()
        answers, questions, message_id, target_employee_id = data['answers'], data['questions'], data['message_id'], data['target_employee_id']
        if len(answers) > 0:
            last_question_id, last_answer = answers[-1]
            await delete_user_answer(message.from_user.id, last_question_id, target_employee_id)
            answers = answers[:-1]
        else:
            last_question_id = questions[0].id
        current_question = await get_question_for_id(last_question_id)
        await state.update_data(answers=answers)
        await handler_question(message, state, current_question, delete_message_id=message_id)
    else:
        await message.answer('Возвращаться некуда', reply_markup=ReplyKeyboardRemove())


@router.message(F.text == 'Отменить')
async def message_cancel_handler(message: Message, state: FSMContext):
    """
    Обработчик клавиши "Отменить"
    """
    current_state = await state.get_state()
    if current_state == ProcessInterview.interview:
        data = await state.get_data()
        answers = data['answers']
        target_employee_id = data['target_employee_id']
        tasks = [delete_user_answer(message.from_user.id, answer[0], target_employee_id) for answer in answers]
        await asyncio.gather(*tasks)

        poll_id = data['poll_id']
        await cancel_poll_status(poll_id, message.from_user.id, target_employee_id)

        last_message_id = data['message_id']
        try:
            await bot.delete_message(message.from_user.id, last_message_id)
        except Exception:
            pass
    await state.clear()
    await message.answer('Отменено', reply_markup=ReplyKeyboardRemove())


@router.message(ProcessInterview.interview)
async def message_interview_handler(message: Message, state: FSMContext):
    """
    Основной хендлер для текстовых ответов
    """
    answer = message.text
    data = await state.get_data()

    poll_status = await get_poll_status(
        poll_id=data['poll_id'],
        telegram_user_id=message.from_user.id,
        target_employee_id=data['target_employee_id'])
    if poll_status is None:
        await message.answer('Этот опрос удален', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        try:
            await message.delete()
        except Exception:
            pass
    elif poll_status == PollStatus.Status.IN_PROGRESS:
        questions, answers, question_id, target_employee_id = data['questions'], data['answers'], data['question_id'], data['target_employee_id']
        question = await get_question_for_id(question_id)
        if question.question_type != 'message':
            temp_message = await message.answer('Выбери ответ на клавиатуре ☝️')
            await message.delete()
            await asyncio.sleep(3)
            await temp_message.delete()
        else:
            answers.append((question_id, answer))
            await save_user_answer(message.from_user.id, question.id, answer, target_employee_id)
            await send_notification_admins(telegram_user_id=message.from_user.id, question=question, answer=answer, target_employee_id=target_employee_id)
            next_question_id = await get_next_question_id(question_id)
            current_question = await get_question_for_id(next_question_id)

            await state.update_data(answers=answers)
            await handler_question(message, state, current_question)
    else:
        await message.answer('Что-то пошло не так', reply_markup=ReplyKeyboardRemove())


@router.message(ProcessRegistration.registration)
async def message_registration_handler(message: Message, state: FSMContext):
    """
    Обработчик для отправленного кода регистрации
    """
    code = message.text
    employee = await get_employee(message.from_user.id)
    if not employee:
        registration = await check_verification_code(message.from_user.id, code)
        answer, employee = registration
        if answer:
            if employee.role == Employee.RoleChoices.EMPLOYEE:
                today = datetime.today().date()
                if employee.date_of_employment >= today:
                    book_employee = get_book('core/management/bot/files/book_employee.pdf')
                    book_welcome = get_book('core/management/bot/files/book_welcome.pdf', welcome=True)
                    curator = await get_curator_for_employee(employee)
                    curator_full_name = curator.full_name if curator else 'Не назначен'
                    await bot.send_document(message.from_user.id,
                                            caption=texts_reg_success_code_employee.format(curator_full_name),
                                            document=book_employee, parse_mode='HTML',
                                            reply_markup=ReplyKeyboardRemove())
                    await bot.send_document(message.from_user.id,
                                            caption='А также предлагаем ознакомиться с нашим Welcome-book',
                                            document=book_welcome)
                else:
                    await bot.send_message(message.from_user.id, text=texts_reg_success_code,
                                           parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
            else:
                await bot.send_message(message.from_user.id, text=texts_reg_success_code,
                                       parse_mode='HTML', reply_markup=ReplyKeyboardRemove())

            await state.clear()

        else:
            await message.answer(texts_reg_invalid_code, parse_mode='HTML')
    else:
        await state.clear()
        await update_telegram_nickname(employee, message.from_user.username)
        if employee.role == Employee.RoleChoices.EMPLOYEE:
            await message.answer(texts_start_is_registered.format(f"@{message.from_user.username}"), parse_mode='HTML',
                                 reply_markup=ReplyKeyboardRemove())
        elif employee.role == Employee.RoleChoices.CURATOR:
            await message.answer(texts_for_curator, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())


@router.message(ProcessHelp.help)
async def message_help_handler(message: Message, state: FSMContext):
    """
    Обработчик отправленного текста пользователем по обратной связи
    """
    user_text = message.text
    await create_feedback_employee(message.from_user.id, user_text)
    await message.answer('Спасибо! Мы свяжемся с тобой в ближайшее время!', reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message()
async def message_without_state_handler(message: Message):
    """
    Вспомогательный обработчик всех остальных сообщений от пользователя, не попадающих в фильтр логики
    """
    employee = await get_employee(message.from_user.id)
    if not employee:
        await message.answer(texts_start_not_registered, parse_mode='HTML', reply_markup=registration_keyboard())
    else:
        await update_telegram_nickname(employee, message.from_user.username)
        if employee.role == Employee.RoleChoices.EMPLOYEE:
            await message.answer(texts_start_is_registered.format(f"@{message.from_user.username}"), parse_mode='HTML',
                                 reply_markup=ReplyKeyboardRemove())
        elif employee.role == Employee.RoleChoices.CURATOR:
            await message.answer(texts_for_curator, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
