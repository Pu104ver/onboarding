from typing import Type

from aiogram.types import BufferedInputFile
from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils import timezone
from django.core.cache import cache

from employees.models import Employee, CuratorEmployees
from projects.models import Project
from questions.models import (
    PollQuestion,
    Question,
    QuestionCondition,
    UserAnswer,
    PollStatus,
    QuestionType, PollType,
)
from feedback.models import FeedbackUser
from slots.models import Slot
from users.utils import verify_token
from core.tasks import notification_admins
from collections import defaultdict
from typing import List, Dict
from django.db.models import QuerySet


@sync_to_async
def get_employee(telegram_user_id) -> Employee | None:
    """
    Функция получения сотрудника
    """
    try:
        employee = Employee.objects.get(telegram_user_id=telegram_user_id)
        return employee
    except ObjectDoesNotExist:
        return None


@sync_to_async
def update_telegram_nickname(employee, current_nickname):
    """
    Обновляет телеграм ник в БД, если он не совпадает с реальным
    """
    if current_nickname and current_nickname != employee.telegram_nickname:
        employee.telegram_nickname = current_nickname
        employee.save()


@sync_to_async
def check_verification_code(
        telegram_user_id: int, code: str
) -> tuple[bool, None] | tuple[bool, Type[Employee]]:
    """
    Функция проверки кода регистрации, если сотрудник существует то записывается его telegram_user_id
    """
    try:
        uid, token = code.split("_")
    except ValueError:
        return False, None
    user = verify_token(uid, token)
    if not user:
        return False, None

    employee = user.employee
    employee.telegram_user_id = telegram_user_id
    employee.save()
    return True, employee


@sync_to_async
def get_curator_for_employee(employee: Employee) -> Employee | None:
    """
    Возвращает самого последнего куратора сотрудника
    """
    try:
        curator_employee = (
            CuratorEmployees.objects.filter(employee=employee).order_by("-id").first()
        )
        if curator_employee:
            return curator_employee.curator
        return None
    except CuratorEmployees.DoesNotExist:
        return None


@sync_to_async
def create_feedback_employee(telegram_user_id, description):
    """
    Создает объект обратной связи и уведомляет админов
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    feedback = FeedbackUser.objects.create(employee=employee, text=description)

    admins = get_admin_telegram_user_id_employee()
    message = (
        f"Обращение от <strong>{employee.full_name}</strong> "
        f"(@{employee.telegram_nickname}):\n"
        f"<strong>{feedback.text}</strong>"
    )
    notification_admins.delay(admins, message)


def update_poll_status_object(
        poll_id: int,
        telegram_user_id: int,
        poll_choices_status: PollStatus.Status,
        target_employee_id=0,
):
    """
    Переводит опрос пользователя в нужный статус
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    poll_status = PollStatus.all_objects.get(
        employee=employee, poll_id=poll_id, target_employee_id=target_employee_id
    )
    if poll_status.status in [PollStatus.Status.NOT_STARTED, PollStatus.Status.EXPIRED]:
        poll_status.started_at = timezone.now()
    poll_status.status = poll_choices_status
    poll_status.save()


@sync_to_async
def cancel_poll_status(
        poll_id: int,
        telegram_user_id: int,
        target_employee_id=0
):
    """
    Отменяет процесс прохождения опросса
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    poll_status = PollStatus.all_objects.get(
        employee=employee, poll_id=poll_id, target_employee_id=target_employee_id
    )
    poll_status.started_at = None

    today = timezone.now().date()
    planned_date = poll_status.date_planned_at

    if planned_date == today:
        poll_status.status = PollStatus.Status.NOT_STARTED
    elif planned_date < today:
        poll_status.status = PollStatus.Status.EXPIRED
    poll_status.save()


@sync_to_async
def completed_poll_status(poll_id, telegram_user_id, target_employee_id=0):
    """
    Помечает опрос пользователя как завершенный
    """
    target_employee_id = None if not target_employee_id else target_employee_id
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    poll_status = PollStatus.all_objects.get(
        employee=employee, poll_id=poll_id, target_employee_id=target_employee_id
    )
    poll_status.status = PollStatus.Status.COMPLETED
    poll_status.completed_at = timezone.now()
    poll_status.save()


@sync_to_async
def get_last_question_and_answer(poll_id, telegram_user_id, target_employee_id=0):
    """
    Возвращает последний вопрос и ответ пользователя по данному опросу.
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    poll = PollQuestion.all_objects.get(id=poll_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    last_answer = (
        UserAnswer.objects.filter(
            employee=employee,
            question__poll=poll,
            target_employee_id=target_employee_id,
        )
        .order_by("-created_at")
        .first()
    )
    if last_answer:
        return last_answer.question, prepared_answer(last_answer.answer)
    first_question = Question.objects.filter(poll=poll).order_by("id").first()
    return first_question, None


@sync_to_async
def get_poll_status(
        poll_id: int, telegram_user_id: int, target_employee_id=0, return_object=False
) -> PollStatus | PollStatus.Status | None:
    """
    Возвращает статус прохождения опроса пользователя
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    try:
        poll_status = PollStatus.all_objects.select_related(
            "poll", "target_employee"
        ).get(employee=employee, poll_id=poll_id, target_employee_id=target_employee_id)
    except PollStatus.DoesNotExist:
        return None
    return poll_status.status if not return_object else poll_status


@sync_to_async
def get_question_to_poll_id(
        poll_id: int, telegram_user_id: int, target_employee_id=0
) -> List[Question]:
    """
    Функция получения списка вопросов для опроса и установление флага опроса в статус "IN_PROGRESS"
    """
    try:
        poll = PollQuestion.all_objects.get(id=poll_id)
        questions = Question.objects.filter(poll=poll)
        update_poll_status_object(
            poll_id, telegram_user_id, PollStatus.Status.IN_PROGRESS, target_employee_id
        )
        return [question for question in questions]
    except ObjectDoesNotExist:
        return []


@sync_to_async
def get_next_question_id(question_id: int, answer="some_text") -> int | None:
    """
    Функция получения следующего вопроса по условию ответа
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return None

    condition = QuestionCondition.objects.filter(
        previous_question=question, answer_condition=answer
    ).first()

    if condition:
        return condition.question.id
    else:
        return None


@sync_to_async
def get_question_for_id(question_id: int) -> Question | None:
    """
    Функция получения вопроса по айдишнику
    """
    try:
        question = Question.objects.get(id=question_id)
        return question
    except ObjectDoesNotExist:
        return None


def get_attention_answers_dict(answer: str) -> dict:
    """
    Масштабируемая функция для выделения "требующих внимания" ответов
    """
    return {
        QuestionType.NUMBERS: ["1", "2", "3"],
        QuestionType.MESSAGE: [answer],
        QuestionType.SLOTS: [answer],
        QuestionType.YES_NO: ["no"],
    }


def get_observable_answers_dict() -> dict:
    """
    Масштабируемая функция для ответов которые переводят сотрудника в статус "Наблюдаемый"
    """
    return {
        QuestionType.NUMBERS: ["1", "2", "3"],
        QuestionType.YES_NO: ["no"],
    }


@sync_to_async
def save_user_answer(telegram_user_id, question_id, answer_text, target_employee_id):
    """
    Функция сохранения ответа от пользователя
    Если ответ "плохой" то помечаем его меткой
    Если ответ уже существует, обновляем его
    """
    question = Question.objects.get(id=question_id)
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)

    code_answer = prepared_answer(answer_text)
    attention_answers = get_attention_answers_dict(code_answer)
    requires_attention = code_answer in attention_answers.get(
        question.question_type, []
    )

    observable_answers = get_observable_answers_dict()
    is_set_observable_risk_status = code_answer in observable_answers.get(
        question.question_type, []
    )

    user_answer = UserAnswer(
        employee=employee,
        question=question,
        answer=answer_text,
        requires_attention=requires_attention,
    )
    if target_employee_id != 0:
        user_answer.target_employee_id = target_employee_id

        target_employee = Employee.objects.get(id=target_employee_id)
        if target_employee.risk_status == Employee.RiskStatus.NOPROBLEM and is_set_observable_risk_status:
            target_employee.risk_status = Employee.RiskStatus.OBSERVABLE
            target_employee.save()
    else:
        if employee.risk_status == Employee.RiskStatus.NOPROBLEM and is_set_observable_risk_status:
            employee.risk_status = Employee.RiskStatus.OBSERVABLE
            employee.save()
    try:
        user_answer.save()
    except IntegrityError:
        if target_employee_id != 0:
            user_answer = UserAnswer.objects.get(
                employee=employee,
                question=question,
                target_employee_id=target_employee_id)
        else:
            user_answer = UserAnswer.objects.get(
                employee=employee,
                question=question)
        user_answer.answer = answer_text
        user_answer.save()


@sync_to_async
def delete_user_answer(telegram_user_id, question_id, target_employee_id=0):
    """
    Функция удаления ответа от пользователя
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    try:
        user_answer = UserAnswer.objects.get(
            employee=employee,
            question_id=question_id,
            target_employee_id=target_employee_id,
        )
        user_answer.delete()
    except Exception:
        pass


@sync_to_async
def booked_slot(telegram_user_id, slot_id):
    """
    Резервирует слот для созвона
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    try:
        slot = Slot.objects.get(id=slot_id)
    except Slot.DoesNotExist:
        return False
    if slot.is_available():
        slot.booked_by = employee
        slot.save()
        return True
    return False


@sync_to_async
def check_completion_previous_poll(
        telegram_user_id: int, poll_id: int, target_employee_id=0
):
    """
    Проверяет статус предыдущих опросов. Возвращает булевое значение - разрешение проходить определенный опрос.
    Ложь если есть непройденный предыдущий опрос, истина в ином случае или если предыдущих опросов не найдено
    """
    employee = Employee.objects.get(telegram_user_id=telegram_user_id)
    target_employee_id = None if not target_employee_id else target_employee_id
    poll_status = PollStatus.all_objects.select_related("poll").get(
        employee=employee, poll_id=poll_id, target_employee_id=target_employee_id
    )

    if (
            poll_status.poll.poll_number == 1 or
            poll_status.created_by_admin or
            poll_status.poll.is_deleted or
            poll_status.poll.poll_type == PollType.INTERMEDIATE_FEEDBACK
    ):
        return True

    previous_poll = PollQuestion.objects.get(
        poll_type=poll_status.poll.poll_type,
        intended_for=employee.role,
        content_type=poll_status.poll.content_type,
        object_id=poll_status.poll.object_id,
        poll_number=poll_status.poll.poll_number - 1,
    )
    try:
        previous_poll_status = PollStatus.all_objects.get(
            employee=employee,
            poll_id=previous_poll.id,
            target_employee_id=target_employee_id,
        )
        return previous_poll_status.status == PollStatus.Status.COMPLETED
    except PollStatus.DoesNotExist:
        return True


def prepared_answer(answer: str) -> str:
    """
    Масштабируемая функция для преобразования в человекочитаемые ответы и обратно.
    """
    mapping = {
        "yes": "Да",
        "no": "Нет",
        "Да": "yes",
        "Нет": "no",
        "slots": "Забронирован слот",
        "Забронирован слот": "slots",
    }
    return mapping.get(answer, answer)


def get_admin_telegram_user_id_employee():
    """
    Получает список telegram_user_id администраторов из кэша или бд
    """
    admins = cache.get("ADMINS_EMPLOYEE")
    if not admins:
        admins = Employee.objects.filter(
            role=Employee.RoleChoices.ADMIN, telegram_user_id__isnull=False
        ).values_list("telegram_user_id", flat=True)
        cache.set("ADMINS_EMPLOYEE", list(admins), timeout=60 * 60 * 12)
    return list(admins)


def generate_message_for_admins(
        telegram_user_id: int, question: Question, answer: str, target_employee_id=0
):
    """
    Проверяет тип вопроса и ответ для генерации сообщения админам
    """
    attention_answers = get_attention_answers_dict(answer)

    if answer in attention_answers.get(question.question_type, []):
        try:
            employee = Employee.objects.get(telegram_user_id=telegram_user_id)
            if target_employee_id:
                target_employee = Employee.objects.get(id=target_employee_id)
                message = (
                    f"Куратор <strong>{employee.full_name}</strong> "
                    f'(@{employee.telegram_nickname}) на вопрос\n"{question.text}"\n'
                    f"по сотруднику <strong>{target_employee.full_name}</strong> (@{target_employee.telegram_nickname})"
                    f'ответил:\n<strong>"{prepared_answer(answer)}"</strong>'
                )
            else:
                message = (
                    f"Сотрудник <strong>{employee.full_name}</strong> "
                    f'(@{employee.telegram_nickname}) на вопрос\n"{question.text}"\n'
                    f'ответил:\n<strong>"{prepared_answer(answer)}"</strong>'
                )
            return message.strip()
        except Employee.DoesNotExist:
            return None
    else:
        return None


def generate_employees_expired_polls_message_for_admins(
        expired_poll_statuses: QuerySet[PollStatus],
) -> str:
    """
    Формирует список сообщений для администраторов о сотрудниках с просроченными опросами.

    Args:
        expired_poll_statuses (QuerySet[PollStatus]): QuerySet с просроченными опросами.

    Returns:
        str: Одно большое сообщение, содержащее информацию о всех сотрудниках и их просроченных опросах.
    """
    if not expired_poll_statuses:
        return None

    employee_polls: Dict[Employee, List[PollQuestion]] = defaultdict(list)

    for poll_status in expired_poll_statuses:
        employee_polls[poll_status.employee].append(poll_status)

    message: str = (
        "<strong>Здравствуйте!</strong>\n"
        "На данный момент некоторые сотрудники имеют просроченные опросы. Их список представлен ниже\U0001F447\n\n"
    )
    message_parts: List[str] = []

    for employee, poll_statuses in employee_polls.items():
        employee_message = f"<strong>Сотрудник: <i>{employee.full_name}</i></strong> (@{employee.telegram_nickname})\nПросроченные опросы:"

        for poll_status in poll_statuses:
            poll_status: PollStatus
            target_employee = poll_status.target_employee
            poll_str = f"<i><strong> - (ID: {poll_status.id})</strong> {poll_status.poll.title} | {poll_status.poll.content_object} | {poll_status.poll.intended_for}</i>"
            employee_message += f"\n{poll_str}"
            employee_message += (
                f" | По сотруднику <strong><i>{target_employee.full_name}</i></strong> (@{target_employee.telegram_nickname})"
                if target_employee
                else ""
            )
        message_parts.append(employee_message)

    message += "\n\n\n".join(message_parts)

    return message.strip()


@sync_to_async
def send_notification_admins(
        telegram_user_id: int,
        question: Question = None,
        answer: str = "",
        target_employee_id=0,
        message: str = "",
):
    """Формирует таску на отправку уведомления админам"""
    if not message:
        message = generate_message_for_admins(
            telegram_user_id, question, answer, target_employee_id
        )
    if message:
        admins = get_admin_telegram_user_id_employee()
        notification_admins.delay(admins, message)
    return None


def get_book(path: str, welcome=False) -> BufferedInputFile:
    """Получает файл для отправки в бота"""
    with open(path, "rb") as file:
        file_data = file.read()
    return BufferedInputFile(file_data, filename="Памятка.pdf" if not welcome else "Welcome_book.pdf")


@sync_to_async
def get_label_content_type(poll, message):
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
