from typing import Union, Optional

from aiogram.filters.callback_data import CallbackData


class PollsIdCF(CallbackData, prefix="polls_id"):
    """
    Фабрика колбэков для кнопок запускающих опросы
    """
    polls_id: int
    target_employee_id: int
    launch_from_list: Optional[bool] = False


class ContinuePollsIdCF(CallbackData, prefix="continue_polls_id"):
    """
    Фабрика колбэков для кнопок "Продолжить"
    """
    polls_id: int
    target_employee_id: Optional[int] = None


class QuestionAnswerCF(CallbackData, prefix='question_answer', sep='^'):
    """
    Фабрика колбэков для кнопок ответов к вопросам
    """
    question_id: int
    args: Union[str, None]
    slot_id: Union[int, None] = None
    slot_time: Union[str, None] = None


class ListPollsCF(CallbackData, prefix="list_polls_id"):
    """
    Фабрика колбэков для генерации списка в зависимости от типа опросов
    """
    polls_type: str = None
    page: Optional[int] = 1
    time_of_day: str = None
