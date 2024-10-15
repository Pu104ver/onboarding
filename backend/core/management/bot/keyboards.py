from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.utils import timezone

from core.management.bot.callback_factory import PollsIdCF, QuestionAnswerCF, ContinuePollsIdCF, ListPollsCF
from employees.models import Employee
from questions.models import KeyboardType, PollStatus, PollType, TimeOfDay
from slots.models import Slot


def interview_start_keyboard(polls_id: int, target_employee: Employee | None):
    """
    Клавиатура приходящая с уведомлением пройти новый опрос
    """
    builder = InlineKeyboardBuilder()
    target_employee_id = target_employee.id if target_employee else 0
    builder.button(text='Ответить на вопросы',
                   callback_data=PollsIdCF(polls_id=polls_id, target_employee_id=target_employee_id))
    return builder.adjust(1).as_markup()


def interview_continue_keyboard(polls_id: int, target_employee: Employee | None):
    """
    Клавиатура приходящая с уведомлением ответить на оставшиеся вопросы
    """
    builder = InlineKeyboardBuilder()
    target_employee_id = target_employee.id if target_employee else 0
    builder.button(text='Продолжить',
                   callback_data=ContinuePollsIdCF(polls_id=polls_id, target_employee_id=target_employee_id))
    return builder.adjust(1).as_markup()


@sync_to_async
def generate_answers_keyboard(question_id, question_type):
    """
    Генератор клавиатуры
    Берет клавиатуру из БД или строит из доступных слотов
    """
    builder = InlineKeyboardBuilder()
    if question_type != 'slots':
        try:
            keyboard_data = KeyboardType.objects.get(question_type=question_type)
            keyboard_json = keyboard_data.keyboard_json
            for btn in keyboard_json['inline_keyboard']:
                builder.button(text=btn['text'],
                               callback_data=QuestionAnswerCF(question_id=question_id, args=str(btn['callback_data'])))
            return builder.adjust(2).as_markup()
        except KeyboardType.DoesNotExist:
            return None
    else:
        today = timezone.now().date()
        slots = Slot.objects.filter(date=today, booked_by=None)
        if slots:
            for btn in slots:
                builder.button(text=btn.start_time,
                               callback_data=QuestionAnswerCF(
                                   question_id=question_id,
                                   args='slots',
                                   slot_id=btn.id,
                                   slot_time=btn.start_time))
        else:
            builder.button(text='Не осталось свободных слотов',
                           callback_data=QuestionAnswerCF(question_id=question_id,
                                                          args=f'slots',
                                                          slot_id=0,
                                                          slot_time='Не выбрано'))
        return builder.adjust(4).as_markup()


def main_keyboard(only_cancel=False):
    """
    Текстовая клавиатура
    """
    if only_cancel:
        kb = [
            [KeyboardButton(text='Отменить'),
             ]
        ]
    else:
        kb = [
            [
                # KeyboardButton(text='Назад'), убрать звездочку, если хотим разрешать возврат
                KeyboardButton(text='Отменить'),
            ],
        ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def registration_keyboard():
    """
    Кнопка регистрации
    """
    builder = InlineKeyboardBuilder()
    builder.button(text='Регистрация', callback_data='registration')
    return builder.adjust(1).as_markup()


def interview_pre_get_list_keyboard(poll_type=None, time_of_day=None):
    """
    Клавиатура приходящая с уведомлением о том что накопилось несколько опросов
    """
    builder = InlineKeyboardBuilder()
    builder.button(text='Пройти опросы',
                   callback_data=ListPollsCF(polls_type=poll_type, time_of_day=time_of_day))
    return builder.adjust(1).as_markup()


@sync_to_async
def generate_list_polls_keyboard(telegram_user_id, poll_type=None, page=1, time_of_day=None):
    """Генерирует клавиатуру списка доступных для прохождения опросов по типу, либо все
    Если опросов более 5, то добавляет пагинационные кнопки"""
    today = timezone.now().date()

    list_poll_type = [poll_type] if poll_type else [PollType.FEEDBACK, PollType.ONBOARDING, PollType.OFFBOARDING,
                                                    PollType.INTERMEDIATE_FEEDBACK]
    time_of_day = [time_of_day] if time_of_day else [TimeOfDay.MORNING, TimeOfDay.EVENING]

    employee = Employee.objects.get(telegram_user_id=telegram_user_id)

    polls_planned = (
        PollStatus.objects.select_related("poll", "employee", "target_employee")
        .filter(
            employee=employee,
            date_planned_at__lte=today,
            status__in=[PollStatus.Status.NOT_STARTED, PollStatus.Status.EXPIRED],
            time_planned_at__in=time_of_day,
            poll__poll_type__in=list_poll_type,
        )
        .order_by("poll__poll_number")
    )
    if not polls_planned:
        return None

    page_size = 5
    start = (page - 1) * page_size
    end = start + page_size

    paginated_polls = polls_planned[start:end]
    builder = InlineKeyboardBuilder()

    label_type = {PollType.ONBOARDING: 'ИС',
                  PollType.FEEDBACK: 'ОС',
                  PollType.OFFBOARDING: 'ОФ',
                  PollType.INTERMEDIATE_FEEDBACK: 'ПОС'}

    for poll_planned in paginated_polls:
        poll = poll_planned.poll
        target_employee = poll_planned.target_employee
        target_employee_id = target_employee.id if target_employee else 0

        if target_employee:
            surname_and_name = ' '.join(target_employee.full_name.split()[:-1])
            text = f'{label_type[poll.poll_type]}: {poll.title} ({surname_and_name[:30]})'
        else:
            text = f'{poll.title}'
        text = text[:60] + '..' if len(text) > 60 else text
        builder.button(text=text,
                       callback_data=PollsIdCF(
                           polls_id=poll.id,
                           target_employee_id=target_employee_id,
                           launch_from_list=True)
                       )

    if page > 1:
        builder.button(
            text="<<",
            callback_data=ListPollsCF(polls_type=poll_type, page=page - 1)
        )
    if end < len(polls_planned):
        builder.button(
            text=">>",
            callback_data=ListPollsCF(polls_type=poll_type, page=page + 1)
        )

    builder.adjust(1)
    return builder.as_markup()
