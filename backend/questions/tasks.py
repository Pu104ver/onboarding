import asyncio
from collections import defaultdict
from datetime import date, timedelta
from typing import List

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from core.management.bot.keyboards import (
    interview_start_keyboard,
    interview_continue_keyboard,
    interview_pre_get_list_keyboard,
)
from core.management.bot.utils.functions import (
    update_poll_status_object,
    generate_employees_expired_polls_message_for_admins,
    get_admin_telegram_user_id_employee,
)
from core.tasks import notification_admins
from employees.models import Employee, CuratorEmployees
from employees.utils import get_curators_as_employees
from projects.models import Project, ProjectAssignment
from .models import PollStatus, PollQuestion, PollType, UserType, TimeOfDay, UserAnswer
from .utils import (
    send_notificate,
    ping_user_to_continue,
    create_similar_poll,
    generate_message_count_polls,
    add_label_content_type_poll,
)


@shared_task
def schedule_notification_poll_onboarding(time_of_day):
    """
    Функция, выполняющаяся в Celery для отправки предложения пройти опрос адаптации на проекте
    """
    today = timezone.now().date()

    # помечаем просроченными старые опросы

    expired_polls = PollStatus.objects.filter(
        date_planned_at__lt=today,
        status=PollStatus.Status.NOT_STARTED,
        poll__poll_type=PollType.ONBOARDING,
    )

    expired_polls.update(status=PollStatus.Status.EXPIRED)
    # обновление статусов опросов сотрудников
    [
        poll.employee.update_onboarding_status()
        for poll in expired_polls
        if poll.target_employee is None
    ]

    polls_planned = (
        PollStatus.objects.select_related("poll", "employee", "target_employee")
        .filter(
            date_planned_at__lte=today,
            time_planned_at=time_of_day,
            status__in=[PollStatus.Status.NOT_STARTED],
            poll__poll_type=PollType.ONBOARDING,
        )
        .order_by("poll__poll_number")
    )

    label_time_of_day = "" if time_of_day == TimeOfDay.MORNING else "(конец дня)"

    polls = defaultdict(list)

    for poll_planned in polls_planned:
        employee: Employee = poll_planned.employee
        poll: PollQuestion = poll_planned.poll
        target_employee: Employee | None = poll_planned.target_employee

        message = (
            poll.message.format(target_employee.full_name)
            if target_employee
            else poll.message
        )
        reply_markup = interview_start_keyboard(poll.id, target_employee)

        message = add_label_content_type_poll(poll, message)

        if employee.telegram_user_id:
            polls[employee.telegram_user_id].append((message, reply_markup))

    loop = asyncio.get_event_loop()

    for telegram_user_id in polls:
        polls_employee = polls[telegram_user_id]
        count_polls = len(polls_employee)
        message, reply_markup = polls_employee[0]
        if count_polls > 1:
            message = generate_message_count_polls(
                count_polls, PollType.ONBOARDING, label_time_of_day
            )
            reply_markup = interview_pre_get_list_keyboard(PollType.ONBOARDING)
        loop.run_until_complete(
            send_notificate(telegram_user_id, message, reply_markup)
        )


@shared_task
def check_poll_status():
    """
    Функция, выполняющаяся в Celery для отправки предложения продолжить опрос
    """
    threshold = timezone.now() - timezone.timedelta(minutes=30)
    stuck_users = PollStatus.objects.filter(
        status=PollStatus.Status.IN_PROGRESS, started_at__lt=threshold
    )
    for record in stuck_users:
        employee: Employee = record.employee
        poll: PollQuestion = record.poll
        target_employee: Employee | None = record.target_employee

        update_poll_status_object(
            poll.id,
            employee.telegram_user_id,
            PollStatus.Status.IN_FROZEN,
            target_employee.id if target_employee else 0,
        )

        reply_markup = interview_continue_keyboard(poll.id, target_employee)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            ping_user_to_continue(employee.telegram_user_id, reply_markup)
        )


@shared_task
def schedule_notification_poll_offboarding():
    """
    Функция, выполняющаяся в Celery для отправки предложения пройти оффбординг
    """
    today = timezone.now().date()

    expired_polls = PollStatus.objects.filter(
        date_planned_at__lt=today,
        status=PollStatus.Status.NOT_STARTED,
        poll__poll_type=PollType.OFFBOARDING,
    )

    expired_polls.update(status=PollStatus.Status.EXPIRED)
    # обновление статусов опросов сотрудников
    [
        poll.employee.update_onboarding_status()
        for poll in expired_polls
        if poll.target_employee is None
    ]

    polls_planned = (
        PollStatus.objects.select_related("poll", "employee", "target_employee")
        .filter(
            date_planned_at__lte=today,
            status__in=[PollStatus.Status.NOT_STARTED],
            poll__poll_type=PollType.OFFBOARDING,
        )
        .order_by("poll__poll_number")
    )

    polls = defaultdict(list)

    for poll_planned in polls_planned:
        employee: Employee = poll_planned.employee
        poll: PollQuestion = poll_planned.poll
        target_employee: Employee | None = poll_planned.target_employee

        message = (
            poll.message.format(target_employee.full_name)
            if target_employee
            else poll.message
        )
        reply_markup = interview_start_keyboard(poll.id, target_employee)

        message = add_label_content_type_poll(poll, message)

        if employee.telegram_user_id:
            polls[employee.telegram_user_id].append((message, reply_markup))

    loop = asyncio.get_event_loop()

    for telegram_user_id in polls:
        polls_employee = polls[telegram_user_id]
        count_polls = len(polls_employee)
        message, reply_markup = polls_employee[0]
        if count_polls > 1:
            message = generate_message_count_polls(count_polls, PollType.OFFBOARDING)
            reply_markup = interview_pre_get_list_keyboard(PollType.OFFBOARDING)
        loop.run_until_complete(
            send_notificate(telegram_user_id, message, reply_markup)
        )


@shared_task
def schedule_notification_poll_feedback(time_of_day, poll_type=PollType.FEEDBACK):
    """
    Функция, выполняющаяся в Celery для отправки предложения пройти опрос обратной связи
    """
    today = timezone.now().date()

    expired_polls = PollStatus.objects.filter(
        date_planned_at__lt=today,
        status=PollStatus.Status.NOT_STARTED,
        poll__poll_type=poll_type,
    )

    expired_polls.update(status=PollStatus.Status.EXPIRED)
    # обновление статусов опросов сотрудников
    [
        poll.employee.update_onboarding_status()
        for poll in expired_polls
        if poll.target_employee is None
    ]

    polls_planned = (
        PollStatus.objects.select_related("poll", "employee", "target_employee")
        .filter(
            date_planned_at__lte=today,
            time_planned_at=time_of_day,
            status__in=[PollStatus.Status.NOT_STARTED],
            poll__poll_type=poll_type,
        )
        .order_by("poll__poll_number")
    )

    label_time_of_day = "" if time_of_day == TimeOfDay.MORNING else "(конец дня)"

    polls = defaultdict(list)

    for poll_planned in polls_planned:
        employee: Employee = poll_planned.employee
        poll: PollQuestion = poll_planned.poll
        target_employee: Employee | None = poll_planned.target_employee

        message = (
            poll.message.format(target_employee.full_name)
            if target_employee
            else poll.message
        )
        reply_markup = interview_start_keyboard(poll.id, target_employee)

        message = add_label_content_type_poll(poll, message)

        if employee.telegram_user_id:
            polls[employee.telegram_user_id].append((message, reply_markup))

    loop = asyncio.get_event_loop()

    for telegram_user_id in polls:
        polls_employee = polls[telegram_user_id]
        count_polls = len(polls_employee)
        message, reply_markup = polls_employee[0]
        if count_polls > 1:
            message = generate_message_count_polls(
                count_polls,
                poll_type,
                label_time_of_day,
            )
            reply_markup = interview_pre_get_list_keyboard(poll_type)
        loop.run_until_complete(
            send_notificate(telegram_user_id, message, reply_markup)
        )


@shared_task
def run_poll_task(poll_status_id):
    """Таска для запуска опроса вручную"""
    poll_status = PollStatus.objects.get(id=poll_status_id)
    chat_id = poll_status.employee.telegram_user_id
    if chat_id:
        message = (
            poll_status.poll.message.format(poll_status.target_employee.full_name)
            if poll_status.target_employee
            else poll_status.poll.message
        )
        message = add_label_content_type_poll(poll_status.poll, message)
        reply_markup = interview_start_keyboard(
            poll_status.poll.id, poll_status.target_employee
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_notificate(chat_id=chat_id, message=message, reply_markup=reply_markup)
        )


@shared_task
def schedule_create_pollstatus_feedback(instance_pk=None, today=None):
    """
    Выполняет создание опросов обратной связи для сотрудников и сотрудников-кураторов
    """

    today = date.today() if today is None else date.fromisoformat(today)

    if not instance_pk:
        employees = Employee.objects.filter(role=Employee.RoleChoices.EMPLOYEE)
        employees = list(employees) + get_curators_as_employees()
    else:
        employees = [Employee.all_objects.get(id=instance_pk)]
    polls = PollQuestion.objects.filter(
        intended_for=UserType.EMPLOYEE,
        poll_type__in=[PollType.FEEDBACK, PollType.INTERMEDIATE_FEEDBACK],
    ).order_by("days_after_hire")

    for employee in employees:
        employee: Employee
        days_passed = (today - employee.date_of_employment).days
        for poll in polls:
            if poll.days_after_hire >= days_passed:
                time_planned_at = poll.time_of_day
                date_planned_at = employee.date_of_employment + timezone.timedelta(
                    days=poll.days_after_hire
                )
                if date_planned_at > today:
                    break
                if date_planned_at == today:
                    PollStatus.objects.get_or_create(
                        employee=employee,
                        poll=poll,
                        target_employee=None,
                        defaults={
                            "time_planned_at": time_planned_at,
                            "date_planned_at": date_planned_at,
                        },
                    )
        employee.update_onboarding_status()


@shared_task
def schedule_create_pollstatus_for_curator(instance_pk=None, today=None):
    """
    Выполняет создание опросов для кураторов
    """

    today = date.today() if today is None else date.fromisoformat(today)

    content_type = ContentType.objects.get_for_model(Project)

    if not instance_pk:
        curator_employees = CuratorEmployees.objects.select_related(
            "curator", "employee"
        ).all()
    else:
        curator_employees = [CuratorEmployees.objects.get(id=instance_pk)]

    feedback_polls = PollQuestion.objects.filter(
        intended_for=UserType.CURATOR,
        poll_type__in=[PollType.FEEDBACK, PollType.INTERMEDIATE_FEEDBACK],
    ).order_by("days_after_hire")

    for instance in curator_employees:
        curator = instance.curator
        employee = instance.employee

        days_passed = (today - employee.date_of_employment).days

        for poll in feedback_polls:
            if poll.days_after_hire >= days_passed:
                time_planned_at = poll.time_of_day
                date_planned_at = employee.date_of_employment + timezone.timedelta(
                    days=poll.days_after_hire
                )
                if date_planned_at > today:
                    break
                if date_planned_at == today:
                    PollStatus.objects.get_or_create(
                        employee=curator,
                        poll=poll,
                        target_employee=employee,
                        defaults={
                            "time_planned_at": time_planned_at,
                            "date_planned_at": date_planned_at,
                        },
                    )

        project_assignments = ProjectAssignment.objects.filter(
            employee=employee
        ).select_related("project")

        for project_assignment in project_assignments:
            if ProjectAssignment.objects.filter(
                employee=curator, project=project_assignment.project
            ).exists():

                onboarding_polls = PollQuestion.objects.filter(
                    intended_for=UserType.CURATOR,
                    poll_type=PollType.ONBOARDING,
                    content_type=content_type,
                    object_id=project_assignment.project.id,
                    days_after_hire__gte=days_passed,
                ).order_by("days_after_hire")

                for poll in onboarding_polls:
                    time_planned_at = poll.time_of_day
                    date_planned_at = (
                        project_assignment.date_of_employment
                        + timezone.timedelta(days=poll.days_after_hire)
                    )
                    if date_planned_at > today:
                        break
                    if date_planned_at == today:
                        PollStatus.objects.get_or_create(
                            employee=curator,
                            poll=poll,
                            target_employee=employee,
                            defaults={
                                "time_planned_at": time_planned_at,
                                "date_planned_at": date_planned_at,
                            },
                        )


@shared_task
def schedule_create_pollstatus_onboarding(instance_pk=None, today=None):
    """
    Выполняет создание опросов адаптации для сотрудника и его кураторов
    """

    today = date.today() if today is None else date.fromisoformat(today)

    content_type = ContentType.objects.get_for_model(Project)
    curators_as_employees = get_curators_as_employees()

    if instance_pk:
        current_project_assignments = [ProjectAssignment.objects.get(id=instance_pk)]
    else:
        current_project_assignments = ProjectAssignment.objects.select_related(
            "project", "employee"
        ).all()

    for current_project_assignment in current_project_assignments:
        if current_project_assignment.date_of_employment is not None and (
            current_project_assignment.employee.role == Employee.RoleChoices.EMPLOYEE
            or current_project_assignment.employee in curators_as_employees
        ):

            project = current_project_assignment.project
            employee = current_project_assignment.employee

            days_passed = (today - current_project_assignment.date_of_employment).days

            polls = PollQuestion.objects.filter(
                intended_for=UserType.EMPLOYEE,
                poll_type=PollType.ONBOARDING,
                content_type=content_type,
                object_id=project.id,
                days_after_hire__gte=days_passed,
            ).order_by("days_after_hire")

            for poll in polls:
                time_planned_at = poll.time_of_day
                date_planned_at = (
                    current_project_assignment.date_of_employment
                    + timezone.timedelta(days=poll.days_after_hire)
                )
                if date_planned_at > today:
                    break
                if date_planned_at == today:
                    PollStatus.objects.get_or_create(
                        employee=employee,
                        poll=poll,
                        target_employee=None,
                        defaults={
                            "time_planned_at": time_planned_at,
                            "date_planned_at": date_planned_at,
                        },
                    )
            employee.update_onboarding_status()

            all_employee_curators = CuratorEmployees.objects.filter(
                employee=employee
            ).values_list("curator_id", flat=True)

            project_curators = ProjectAssignment.objects.filter(
                project=project, employee__in=all_employee_curators
            ).values_list("employee_id", flat=True)

            polls_curator = PollQuestion.objects.filter(
                intended_for=UserType.CURATOR,
                poll_type=PollType.ONBOARDING,
                content_type=content_type,
                object_id=project.id,
                days_after_hire__gte=days_passed,
            ).order_by("days_after_hire")

            for curator_id in project_curators:
                for poll in polls_curator:
                    time_planned_at = poll.time_of_day
                    date_planned_at = (
                        current_project_assignment.date_of_employment
                        + timezone.timedelta(days=poll.days_after_hire)
                    )
                    if date_planned_at > today:
                        break
                    if date_planned_at == today:
                        PollStatus.objects.get_or_create(
                            employee_id=curator_id,
                            poll=poll,
                            target_employee=employee,
                            defaults={
                                "time_planned_at": time_planned_at,
                                "date_planned_at": date_planned_at,
                            },
                        )


@shared_task
def create_need_pollquestion_feedback(instance_pk=None, poll_type=PollType.FEEDBACK):
    """Если в базе данных появляется сотрудник с очень старой датой устройства, то создаем недостающие
    шаблоны опросов по последнему шаблону"""

    today = date.today()

    if not instance_pk:
        oldest_employee = Employee.objects.order_by("date_of_employment").first()
    else:
        oldest_employee = Employee.objects.get(id=instance_pk)

    last_pollquestion = (
        PollQuestion.objects.filter(poll_type=poll_type, intended_for=UserType.EMPLOYEE)
        .order_by("-days_after_hire")
        .first()
    )

    last_pollquestion_for_curator = (
        PollQuestion.objects.filter(poll_type=poll_type, intended_for=UserType.CURATOR)
        .order_by("-days_after_hire")
        .first()
    )

    days_worked = (today - oldest_employee.date_of_employment).days
    poll_number = last_pollquestion.poll_number
    poll_number_curator = last_pollquestion_for_curator.poll_number
    days_after_hire = last_pollquestion.days_after_hire

    while days_worked > days_after_hire:
        if poll_type == PollType.FEEDBACK:
            days_after_hire += 90
        else:
            days_after_hire += 30
            if days_after_hire % 90 == 0:
                continue

        month_title = days_after_hire // 30
        poll_number += 1
        poll_number_curator += 1

        new_pollquestion = PollQuestion.objects.create(
            title=f"{month_title}-й месяц",
            message=f"Привет! Сегодня {month_title} месяцев, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=days_after_hire,
            time_of_day=TimeOfDay.MORNING,
            poll_type=poll_type,
            poll_number=poll_number,
        )

        create_similar_poll(last_pollquestion, new_pollquestion)

        new_pollquestion_curator = PollQuestion.objects.create(
            title=f"{month_title}-й месяц",
            message="Здравствуйте! c Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=days_after_hire,
            time_of_day=TimeOfDay.MORNING,
            intended_for=UserType.CURATOR,
            poll_type=poll_type,
            poll_number=poll_number_curator,
        )
        create_similar_poll(last_pollquestion_for_curator, new_pollquestion_curator)


@shared_task
def admin_notification_employees_expired_polls():
    """
    Celery задача, которая посылает уведомление админам о просроченных опросах
    Уведолмение состоит из списка сотрудников и их просроченных опросов
    """
    expired_poll_statuses = (
        PollStatus.objects.filter(status=PollStatus.Status.EXPIRED)
        .select_related("employee", "target_employee", "poll")
        .exclude(poll__poll_type=PollType.INTERMEDIATE_FEEDBACK)
        .distinct()
    )

    if not expired_poll_statuses:
        return

    message = generate_employees_expired_polls_message_for_admins(expired_poll_statuses)
    admins = get_admin_telegram_user_id_employee()
    notification_admins.delay(admins, message)


@shared_task
def schedule_ping_notification_polls():
    """Таска для напоминания пользователю о просроченных опросах"""
    today = timezone.now().date()

    polls_planned = (
        PollStatus.objects.filter(
            date_planned_at__lte=today,
            status__in=[PollStatus.Status.EXPIRED],
        ).exclude(poll__poll_type=PollType.INTERMEDIATE_FEEDBACK)
    ).select_related("employee")

    polls = defaultdict(int)

    for poll_planned in polls_planned:
        employee: Employee = poll_planned.employee
        if employee.telegram_user_id:
            polls[employee.telegram_user_id] += 1

    loop = asyncio.get_event_loop()

    for telegram_user_id in polls:
        count_polls = polls[telegram_user_id]
        if count_polls == 1:
            count_text = f"{count_polls} просроченный опрос"
        elif 1 < count_polls <= 4:
            count_text = f"{count_polls} просроченных опроса"
        else:
            count_text = f"{count_polls} просроченных опросов"
        message = f"У вас есть {count_text}"
        loop.run_until_complete(
            send_notificate(
                telegram_user_id, message, interview_pre_get_list_keyboard()
            )
        )


@shared_task
def schedule_create_pollstatuses(list_days: None | List[date] = None):
    """Таска создающая опросы на сегодняшний и предыдущий день"""
    if not list_days:
        today = date.today()
        yesterday = today - timedelta(days=1)
        list_days = [today, yesterday]

    list_days = [day.isoformat() for day in list_days]
    for day in list_days:
        task_name = f"create_pollstatuses_{day}"
        if not cache.get(task_name):
            eta = timezone.now().replace(hour=1, minute=0, second=0, microsecond=0)

            schedule_create_pollstatus_onboarding.apply_async(args=[None, day], eta=eta)
            schedule_create_pollstatus_feedback.apply_async(args=[None, day], eta=eta)
            schedule_create_pollstatus_for_curator.apply_async(
                args=[None, day], eta=eta
            )

            cache.set(task_name, "scheduled", timeout=timedelta(days=5).total_seconds())
        else:
            pass


@shared_task
def cancel_frozen_pollstatuses():
    """Если опрос остался замороженным, то сбрасываем его состояние в не начат, и удаляем уже данные ответы"""

    pollstatuses_frozen = PollStatus.objects.filter(
        status=PollStatus.Status.IN_FROZEN
    ).select_related("employee", "target_employee", "poll")

    for poll_status in pollstatuses_frozen:
        with transaction.atomic():

            user_answers = UserAnswer.objects.filter(
                question__poll=poll_status.poll,
                employee=poll_status.employee,
                target_employee=poll_status.target_employee,
            )
            if user_answers:
                user_answers.delete()

            poll_status.status = PollStatus.Status.NOT_STARTED
            poll_status.save()
            employee: Employee = poll_status.employee
            employee.update_onboarding_status()
