from datetime import date

from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from comments.models import Comment
from core.management.bot.texts import texts_add_new_employee_for_curator
from employees.models import Employee, CuratorEmployees
from employees.tasks import send_planned_meeting_notification, send_notification_curator
from questions.models import PollStatus, PollQuestion, PollType, UserType
from projects.models import ProjectAssignment
from feedback.models import FeedbackUser
from questions.tasks import (
    schedule_create_pollstatus_feedback,
    schedule_create_pollstatus_for_curator,
    create_need_pollquestion_feedback,
)


@receiver(pre_save, sender=Employee)
def handle_employee_dismission(sender, instance: Employee, **kwargs):
    """
    Сигнал при котором создается будущий опрос для сотрудника.
    Если у него устанавливается дата увольнения - меняем статус сотрудника на Оффбординг
    """
    if instance.pk:
        try:
            current_employee: Employee = Employee.all_objects.get(pk=instance.pk)
            if (
                current_employee.date_of_dismission != instance.date_of_dismission
                and current_employee.date_of_dismission is None
            ):
                PollStatus.objects.filter(
                    Q(employee=instance) | Q(target_employee=instance)
                ).update(is_archived=True)

                polls = PollQuestion.objects.filter(
                    intended_for=UserType.EMPLOYEE,
                    poll_type=PollType.OFFBOARDING,
                )
                for poll in polls:
                    PollStatus.objects.get_or_create(
                        employee=instance,
                        poll=poll,
                        date_planned_at=instance.date_of_dismission,
                        time_planned_at=poll.time_of_day,
                        target_employee=None,
                    )
                instance.status = Employee.EmployeeStatus.OFFBOARDING
        except Employee.DoesNotExist:
            pass


@receiver(post_save, sender=Employee)
def handle_employee_deletion(sender, instance: Employee, **kwargs):
    """
    Если сотрудник был помечен как удаленный:
    - Удаляет комментарии
    - Удаляет фидбеки
    - Удаляет запланированные опросы сотрудника и его кураторов
    - Разрывает все связи с кураторами/сотрудниками и проектами
    """
    if instance.is_deleted:
        Comment.objects.filter(Q(employee=instance) | Q(author=instance)).delete()

        FeedbackUser.objects.filter(employee=instance).hard_delete()

        # из-за этого сигнала нельзя создать post_delete сигнал для модели PollStatus, чтобы обновлялся статус сотрудника после удаления объекта PollStatus
        PollStatus.objects.filter(
            Q(employee=instance) | Q(target_employee=instance)
        ).delete()

        CuratorEmployees.objects.filter(Q(employee=instance) | Q(curator=instance)).delete()

        ProjectAssignment.objects.filter(employee=instance).delete()


@receiver(post_save, sender=Employee)
def delete_pollstatus_on_archived(sender, instance: Employee, **kwargs):
    """
    Переносит в архив запланированные опросы сотрудника и его кураторов если он помещается в архив
    """
    if instance.is_archived:
        PollStatus.objects.filter(
            Q(employee=instance) | Q(target_employee=instance)
        ).update(is_archived=True)


@receiver(post_save, sender=Employee)
def handle_employee_creation(sender, instance: Employee, created, **kwargs):
    """
    Сигнал, который срабатывает при создании сотрудника
    Планирует для него опросы обратной связи и промежуточной обратной связи
    Выставляет нужный статус в зависимости от даты первого рабочего дня
    """
    if created:
        if instance.date_of_employment:
            today = date.today()
            days_passed = (today - instance.date_of_employment).days
            if days_passed > (3 * 30):
                instance.status = Employee.EmployeeStatus.ADAPTED
                instance.save()
        create_need_pollquestion_feedback.delay(instance.pk, PollType.FEEDBACK)
        create_need_pollquestion_feedback.delay(instance.pk, PollType.INTERMEDIATE_FEEDBACK)
        schedule_create_pollstatus_feedback.delay(instance.pk)


@receiver(post_save, sender=CuratorEmployees)
def handle_curator_employee_assignment(sender, instance: CuratorEmployees, created, **kwargs):
    """
    Сигнал, который срабатывает при добавлении нового куратора к сотруднику.
    Планирует опросы обратной связи для куратора по сотруднику
    Также планирует опросы адаптации по проекту и сотруднику для куратора
    """
    if created:
        today = date.today()
        schedule_create_pollstatus_for_curator.delay(instance.pk)
        curator = instance.curator
        employee = instance.employee
        if curator.telegram_user_id and employee.date_of_employment >= today:
            text_message = texts_add_new_employee_for_curator.format(
                employee.date_of_employment,
                employee.full_name,
                employee.telegram_nickname,
            )
            send_notification_curator.delay(curator.telegram_user_id, text_message)


@receiver(pre_save, sender=Employee)
def send_meeting_notification(sender, instance: Employee, **kwargs):
    """
    Сигнал для отправки уведомления сотруднику в Telegram бота при установке даты встречи по итогам ИС
    """
    if instance.pk:
        try:
            current_employee = Employee.objects.get(pk=instance.pk)
            if (
                current_employee.date_meeting != instance.date_meeting
                and instance.date_meeting is not None
            ):
                rescheduled = False if current_employee.date_meeting is None else True
                if instance.telegram_user_id:
                    send_planned_meeting_notification.delay(
                        instance.telegram_user_id, instance.date_meeting, rescheduled
                    )
        except Employee.DoesNotExist:
            pass
