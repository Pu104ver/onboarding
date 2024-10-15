from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.management.bot.create_bot import bot
from core.management.bot.keyboards import generate_answers_keyboard, main_keyboard, generate_list_polls_keyboard
from core.management.bot.states import ProcessInterview, ProcessRegistration
from core.management.bot.texts import texts_reg_need_code
from core.management.bot.utils.functions import get_question_to_poll_id, \
    get_question_for_id, get_next_question_id, save_user_answer, get_poll_status, completed_poll_status, \
    get_last_question_and_answer, booked_slot, get_employee, update_telegram_nickname, check_completion_previous_poll, \
    prepared_answer, send_notification_admins, get_label_content_type
from core.management.bot.callback_factory import PollsIdCF, QuestionAnswerCF, ContinuePollsIdCF, ListPollsCF
from questions.models import PollStatus

router = Router(name='callbacks-router')


async def handler_question(callback: CallbackQuery, state: FSMContext, current_question, is_start=False, last_data=None, start_message_text=None):
    """
    Функция обработки нового вопроса
    """
    keyboard = await generate_answers_keyboard(question_id=current_question.id, question_type=current_question.question_type)
    if is_start:
        await callback.message.delete()
        start_message = await bot.send_message(callback.from_user.id, start_message_text, reply_markup=main_keyboard())
        message = await bot.send_message(callback.from_user.id, current_question.text, reply_markup=keyboard)
        await state.update_data(temp_message_id=start_message.message_id)
    else:
        await callback.message.edit_text(last_data)
        message = await bot.send_message(callback.from_user.id, current_question.text, reply_markup=keyboard)
    if current_question.question_type == 'finish':
        data = await state.get_data()
        await completed_poll_status(poll_id=data['poll_id'],
                                    telegram_user_id=callback.from_user.id,
                                    target_employee_id=data['target_employee_id'])
        await state.clear()
        await bot.delete_message(callback.from_user.id, data['temp_message_id'])
    else:
        await state.update_data(question_id=current_question.id, message_id=message.message_id)


@router.callback_query(PollsIdCF.filter())
async def start_interview_handler(callback: CallbackQuery, callback_data: PollsIdCF, state: FSMContext):
    """
    Хендлер начала опроса
    """
    current_state = await state.get_state()
    poll_status = await get_poll_status(
        poll_id=callback_data.polls_id,
        telegram_user_id=callback.from_user.id,
        target_employee_id=callback_data.target_employee_id,
        return_object=True
    )

    if poll_status is None:
        await callback.answer('Этот опрос удален', show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return
    previous_is_completed = await check_completion_previous_poll(callback.from_user.id, callback_data.polls_id, callback_data.target_employee_id)
    if current_state is None and poll_status.status != PollStatus.Status.COMPLETED and previous_is_completed:
        questions = await get_question_to_poll_id(
            poll_id=callback_data.polls_id,
            telegram_user_id=callback.from_user.id,
            target_employee_id=callback_data.target_employee_id)
        await state.set_state(ProcessInterview.interview)
        await state.update_data(questions=questions,
                                answers=[],
                                poll_id=callback_data.polls_id,
                                target_employee_id=callback_data.target_employee_id)
        current_question = questions[0]

        launch_from_list = callback_data.launch_from_list
        if not launch_from_list:
            start_message_text = 'Секунду...'
        else:
            start_message_text = poll_status.poll.message
            if poll_status.target_employee:
                start_message_text = start_message_text.format(poll_status.target_employee.full_name)
            start_message_text = await get_label_content_type(poll_status.poll, start_message_text)

        await handler_question(callback, state, current_question, is_start=True, start_message_text=start_message_text)
    elif poll_status.status == PollStatus.Status.COMPLETED:
        await callback.answer('Этот опрос уже пройден', show_alert=True)
    elif current_state is not None:
        await callback.answer('Необходимо сначала закончить предыдущее действие или опрос', show_alert=True)
    else:
        await callback.answer('Прежде чем начать этот опрос, необходимо завершить предыдущий', show_alert=True)


@router.callback_query(QuestionAnswerCF.filter(), ProcessInterview.interview)
async def process_interview_handler(callback: CallbackQuery, callback_data: QuestionAnswerCF, state: FSMContext):
    """
    Основной хендлер обработки кнопочных ответов
    """
    data = await state.get_data()
    poll_status = await get_poll_status(
        poll_id=data['poll_id'],
        telegram_user_id=callback.from_user.id,
        target_employee_id=data['target_employee_id']
    )
    if poll_status is None:
        await callback.answer('Этот опрос удален', show_alert=True)
        await state.clear()
        try:
            await callback.message.delete()
        except Exception:
            pass
    elif poll_status == PollStatus.Status.IN_PROGRESS:
        answer = callback_data.args
        if answer == 'slots' and callback_data.slot_id != 0:
            booked_result = await booked_slot(callback.from_user.id, callback_data.slot_id)
            if not booked_result:
                await callback.answer('Этот слот уже занят', show_alert=True)
                return
        questions, answers, target_employee_id = data['questions'], data['answers'], data['target_employee_id']
        question_id = callback_data.question_id
        answers.append((question_id, answer))
        question = await get_question_for_id(question_id)
        await save_user_answer(callback.from_user.id, question.id, prepared_answer(answer), target_employee_id)

        await send_notification_admins(telegram_user_id=callback.from_user.id, question=question, answer=answer, target_employee_id=target_employee_id)
        next_question_id = await get_next_question_id(question_id, answer)
        current_question = await get_question_for_id(next_question_id)

        await state.update_data(answers=answers)

        if callback_data.slot_time:
            last_question_data = question.text + f'\n\nВыбранное время: {callback_data.slot_time}'
        elif question.show:
            last_question_data = question.text + f'\n\nВаш ответ: {prepared_answer(answer)}'
        else:
            last_question_data = question.text

        await handler_question(callback, state, current_question, last_data=last_question_data)
    else:
        await callback.answer('Что-то пошло не так', show_alert=True)
        await state.clear()
        try:
            await callback.message.delete()
        except Exception:
            pass


@router.callback_query(F.data == 'registration')
async def process_registration(callback: CallbackQuery, state: FSMContext):
    """
    Обработка нажатия клавиши Регистрация
    """
    employee = await get_employee(callback.from_user.id)
    if not employee:
        await callback.answer()
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, texts_reg_need_code, reply_markup=main_keyboard(only_cancel=True), parse_mode='HTML')
        await state.set_state(ProcessRegistration.registration)
    else:
        await update_telegram_nickname(employee, callback.from_user.username)
        await callback.answer('Регистрация уже пройдена', show_alert=True)
        await callback.message.delete()


@router.callback_query(ContinuePollsIdCF.filter())
async def continue_process_interview_handler(callback: CallbackQuery, callback_data: ContinuePollsIdCF, state: FSMContext):
    """
    Хендлер кнопки "Продолжить" - возвращает пользователя к вопросу на котором он остановился отвечать
    """
    poll_id = callback_data.polls_id
    await state.clear()
    poll_status = await get_poll_status(
        poll_id=poll_id,
        telegram_user_id=callback.from_user.id,
        target_employee_id=callback_data.target_employee_id
    )
    if poll_status is None:
        await callback.answer('Этот опрос удален', show_alert=True)
        await state.clear()
        try:
            await callback.message.delete()
        except Exception:
            pass
    elif poll_status == PollStatus.Status.IN_FROZEN:
        data = await get_last_question_and_answer(poll_id, callback.from_user.id, callback_data.target_employee_id)
        last_question, last_answer = data
        await state.set_state(ProcessInterview.interview)
        questions = await get_question_to_poll_id(
            poll_id=poll_id,
            telegram_user_id=callback.from_user.id,
            target_employee_id=callback_data.target_employee_id
        )
        await state.update_data(questions=questions,
                                answers=[],
                                poll_id=poll_id,
                                target_employee_id=callback_data.target_employee_id)

        if last_answer is None:
            current_question = last_question
        else:
            next_question_id = await get_next_question_id(last_question.id, last_answer)
            current_question = await get_question_for_id(next_question_id)
        await handler_question(callback, state, current_question, is_start=True)
    else:
        await callback.answer('Этот опрос уже недоступен', show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass


@router.callback_query(ListPollsCF.filter())
async def get_list_for_type_interview_handler(callback: CallbackQuery, state: FSMContext, callback_data: ListPollsCF):
    """
    Высылает пользователю его непройденные опросы по типу опросов
    """
    current_state = await state.get_state()
    if current_state is None:
        polls_type = callback_data.polls_type
        page = callback_data.page
        time_of_day = callback_data.time_of_day
        list_polls_keyboard = await generate_list_polls_keyboard(callback.from_user.id, polls_type, page, time_of_day)
        if list_polls_keyboard is None:
            await callback.message.edit_text('На данный момент все опросы пройдены')
        else:
            try:
                await callback.message.edit_text('Ваши непройденные опросы 👇')
            except:
                pass
            await callback.message.edit_reply_markup(reply_markup=list_polls_keyboard)

    else:
        await callback.answer('Необходимо сначала закончить предыдущее действие или опрос', show_alert=True)


@router.callback_query()
async def answer_without_state_handler(callback: CallbackQuery, state: FSMContext):
    """
    Вспомогательный хендлер-заглушка если пользователь что-то нажимает в старых сообщениях
    """
    await callback.answer('Что-то пошло не так', show_alert=True)
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass




