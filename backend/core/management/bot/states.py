from aiogram.fsm.state import State, StatesGroup


class ProcessInterview(StatesGroup):
    """
    Состояние бота "В процессе опроса"
    """
    interview = State()


class ProcessRegistration(StatesGroup):
    """
    Состояние бота "В процессе регистрации"
    """
    registration = State()


class ProcessHelp(StatesGroup):
    """
    Состояние бота "В процессе обратной связи"
    """
    help = State()