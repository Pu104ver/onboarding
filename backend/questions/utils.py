from typing import List

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from core.management.bot.create_bot import bot
from projects.models import Project
from questions.models import Question, QuestionType, QuestionCondition, PollType


async def send_notificate(chat_id: int | None, message: str, reply_markup: InlineKeyboardMarkup | None = None):
    """
    Отправляет сообщение в бота с предложением пройти опрос
    """
    if chat_id:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup
            )
        except Exception:
            pass


async def ping_user_to_continue(chat_id: int | None, reply_markup: InlineKeyboardMarkup):
    """
    Отправляет сообщения в бота с предложением закончить опрос
    """
    if chat_id:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text='Ты на связи?',
                reply_markup=ReplyKeyboardRemove()
            )
            await bot.send_message(
                chat_id=chat_id,
                text='Пожалуйста, заверши опрос до конца',
                reply_markup=reply_markup
            )
        except Exception:
            pass


def create_questions(poll, list_questions: list) -> List[int]:
    """
    Создает вопросы для опроса
    """
    questions_object = []
    for question_data in list_questions:
        flag_show = question_data[1] in [
            QuestionType.YES_NO, QuestionType.MESSAGE, QuestionType.NUMBERS, QuestionType.SLOTS
        ]
        category_analytics = question_data[2] if len(question_data) > 2 else None
        questions_object.append(
            Question(
                text=question_data[0],
                question_type=question_data[1],
                poll=poll,
                show=flag_show,
                category_analytics=category_analytics
            )
        )
    Question.objects.bulk_create(questions_object)
    return [question.id for question in questions_object]


def create_conditions(list_conditions: list):
    """
    Создает цепочку переходов для вопросов
    """
    conditions_to_create = []
    for condition_data in list_conditions:
        conditions_to_create.append(
            QuestionCondition(
                question_id=condition_data[0],
                previous_question_id=condition_data[1],
                answer_condition=condition_data[2],
            )
        )
    QuestionCondition.objects.bulk_create(conditions_to_create)


def create_similar_poll(last_poll, new_poll):
    """
    Создает новый опрос, похожий на существующий, с сохранением всех вопросов и условий вопросов.
    """
    with transaction.atomic():
        question_mapping = {}

        for question in last_poll.questions.all():
            new_question = Question.objects.create(
                poll=new_poll,
                text=question.text,
                question_type=question.question_type,
                show=question.show,
            )
            question_mapping[question.id] = new_question

        for condition in QuestionCondition.objects.filter(
            previous_question__poll=last_poll
        ):
            new_condition = QuestionCondition.objects.create(
                question=question_mapping[condition.question.id],
                previous_question=question_mapping[condition.previous_question.id],
                answer_condition=condition.answer_condition,
            )

    return new_poll


def generate_message_count_polls(count_polls: int, poll_type: PollType, label_time_of_day: str = '') -> str:
    """Генерирует понятное сообщение о непройденных опросах для пользователя"""
    poll_type_to_str = {
        PollType.ONBOARDING: 'испытательного срока',
        PollType.FEEDBACK: 'обратной связи',
        PollType.OFFBOARDING: 'оффбординга',
        PollType.INTERMEDIATE_FEEDBACK: 'промежуточной обратной связи'
    }
    if count_polls == 1:
        poll = 'непройденный опрос'
    else:
        poll = 'непройденные опросы'
    return f'У вас есть {poll} {poll_type_to_str[poll_type]} {label_time_of_day}'


def add_label_content_type_poll(poll, message):
    """Формирует приписку к опросу для указания источника опроса"""

    if poll.content_type is None:
        if poll.poll_type == PollType.FEEDBACK:
            message = message + f"\n\n(Обратная связь)"
        elif poll.poll_type == PollType.INTERMEDIATE_FEEDBACK:
            message = message + f"\n\n(Промежуточная обратная связь)"
        elif poll.poll_type == PollType.OFFBOARDING:
            message = message + f"\n\n(Оффбординг)"
    elif poll.content_type == ContentType.objects.get_for_model(Project):
        project = Project.objects.get(id=poll.object_id)
        message = message + f"\n\n(Проект: {project.name})"
    return message
