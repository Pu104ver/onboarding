from django.conf import settings
from django.db import models
from django.utils import timezone
from core.models import SoftDeleteModel
from questions.models import PollStatus, PollType
from employees.managers import EmployeeManager


class Employee(SoftDeleteModel):
    """
    Модель сотрудника.

    Attributes:
        user (OneToOneField): Ссылка на пользователя.
        full_name (CharField): Полное имя сотрудника.
        role (CharField): Роль сотрудника (администратор, hr, куратор, сотрудник).
        telegram_nickname (CharField): Ник в Telegram.
        telegram_user_id (IntegerField): ID пользователя в Telegram.
        date_of_employment (DateField): Дата первого рабочего дня.
        date_of_dismission (DateField): Дата увольнения сотрудника.
        description (TextField): Описание сотрудника.
        is_archived (BooleanField): Флаг, указывающий, что сотрудник находится в архиве.
        created_by (ForeignKey): Пользователь, создавший запись.
        created_at (DateTimeField): Дата и время создания записи.
        updated_by (ForeignKey): Пользователь, последний обновивший запись.
        updated_at (DateTimeField): Дата и время последнего обновления записи.
        status (CharField): Статус сотрудника в системе
        risk_status (CharField): Статус риска сотрудника в системе
        date_meeting (DateTimeField): Дата и время встречи по итогам ИС
        is_curator_employee (BooleanField): Флаг, указывающий, что сотрудник является и куратором, и сотрудником
        onboarding_status (ForeignKey): Статус опроса сотрудника.
    """

    class RoleChoices(models.TextChoices):
        ADMIN = "admin", "Администратор"
        HR = "hr", "HR"
        CURATOR = "curator", "Куратор"
        EMPLOYEE = "employee", "Сотрудник"

    class EmployeeStatus(models.TextChoices):
        ONBOARDING = "onboarding", "Испытательный срок"
        OFFBOARDING = "offboarding", "Оффбординг"
        ADAPTED = "adapted", "Адаптированный"
        FIRED = "fired", "Уволен"

    class RiskStatus(models.TextChoices):
        RISKZONE = "riskzone", "В зоне риска"
        OBSERVABLE = "observable", "Наблюдаемый"
        NOPROBLEM = "noproblem", "Без проблем"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.EMPLOYEE,
        verbose_name="Роль сотрудника",
    )
    full_name = models.CharField(max_length=255, default="ФИО", verbose_name="ФИО")
    telegram_nickname = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Ник в Telegram"
    )

    telegram_user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Telegram ID пользователя",
        unique=True,
    )

    date_of_employment = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата первого рабочего дня",
    )

    date_of_dismission = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата увольнения",
    )

    description = models.CharField(
        max_length=125,
        null=True,
        blank=True,
        verbose_name="О сотруднике",
    )

    is_archived = models.BooleanField(default=False, verbose_name="В архиве")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="created_employees",
        on_delete=models.SET_NULL,
        verbose_name="Создано пользователем",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_employees",
        on_delete=models.SET_NULL,
        verbose_name="Обновлено пользователем",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ONBOARDING,
        verbose_name="Статус сотрудника",
    )

    risk_status = models.CharField(
        max_length=20,
        choices=RiskStatus.choices,
        default=RiskStatus.NOPROBLEM,
        verbose_name="Статус риска",
    )

    date_meeting = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Встреча по итогам ИС",
    )

    is_curator_employee = models.BooleanField(
        default=False, verbose_name="Куратор-сотрудник"
    )

    onboarding_status = models.ForeignKey(
        PollStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Статус опроса сотрудника",
        related_name="employee_onboarding_status",
    )

    def update_onboarding_status(self):
        """
        Обновление статуса опроса сотрудника.

        Вычисляется по личным опросам сотрудника. Сортируется по дате прохождения и статусу прохождения.
        Необходимо вызывать при создании, обновлении, удалении PollStatus, привязанного к сотруднику (личный опрос).
        """
        
        poll_statuses = (
            PollStatus.objects.exclude(poll__poll_type=PollType.INTERMEDIATE_FEEDBACK)
            .filter(
                employee=self,
                target_employee__isnull=True,
                date_planned_at__lte=timezone.now(),
            )
            .order_by("date_planned_at")
        )
        
        if not poll_statuses:
            self.onboarding_status = None
            self.save()
            return None

        priority_statuses = [
            PollStatus.Status.EXPIRED,
            PollStatus.Status.IN_FROZEN,
            PollStatus.Status.IN_PROGRESS,
            PollStatus.Status.NOT_STARTED,
        ]

        for status in priority_statuses:
            poll_status: PollStatus = poll_statuses.filter(status=status).first()
            if poll_status:
                self.onboarding_status = poll_status
                self.save()
                return None

        last_poll_status: PollStatus = poll_statuses.last()
        self.onboarding_status = last_poll_status
        self.save()

    objects: EmployeeManager = EmployeeManager()

    def save(self, *args, **kwargs):
        if self.telegram_nickname:
            self.telegram_nickname = self.telegram_nickname.lstrip("@")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.full_name} ({str(self.user)})"


class CuratorEmployees(models.Model):
    """
    Модель для связи кураторов и сотрудников.

    Attributes:
        curator (ForeignKey): Ссылка на куратора (сотрудника).
        employee (ForeignKey): Ссылка на сотрудника.
    """

    curator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employees",
        verbose_name="Куратор",
        limit_choices_to={"role": Employee.RoleChoices.CURATOR},
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="curators",
        verbose_name="Сотрудник",
        limit_choices_to={"role": Employee.RoleChoices.EMPLOYEE},
    )

    class Meta:
        unique_together = ("curator", "employee")
        verbose_name = "Куратор сотрудника"
        verbose_name_plural = "Кураторы сотрудников"

    def __str__(self):
        return f"{self.curator.full_name} курирует {self.employee.full_name}"
