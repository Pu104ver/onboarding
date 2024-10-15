from django.db import models
from django.conf import settings
from employees.models import Employee
from core.models import SoftDeleteModel


class Project(SoftDeleteModel):
    """
    Модель проекта.

    Attributes:
        name (CharField): Название проекта.
        date_start (DateField): Дата начала проекта.
        date_end (DateField): Дата окончания проекта.
        created_by (ForeignKey): Пользователь, создавший запись.
        created_at (DateTimeField): Дата и время создания записи.
        updated_by (ForeignKey): Пользователь, последний обновивший запись.
        updated_at (DateTimeField): Дата и время последнего обновления записи.
    """

    name = models.CharField(max_length=255, verbose_name="Название проекта")

    date_start = models.DateField(
        null=True, blank=True, verbose_name="Дата начала проекта"
    )

    date_end = models.DateField(
        null=True, blank=True, verbose_name="Дата окончания проекта"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects",
        verbose_name="Создано пользователем",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_projects",
        verbose_name="Обновлено пользователем",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"


class ProjectAssignment(models.Model):
    """
    Промежуточная модель для связи сотрудников и проектов.

    Attributes:
        employee (ForeignKey): Ссылка на сотрудника.
        project (ForeignKey): Ссылка на проект.
        date_of_employment (DateField): Дата первого рабочего дня на проекте.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="projects_assigned",
        verbose_name="Сотрудник",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="employees_assigned",
        verbose_name="Проект",
    )

    date_of_employment = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата первого рабочего дня на проекте",
    )

    class Meta:
        unique_together = ("employee", "project")
        verbose_name = "Назначение сотрудника на проект"
        verbose_name_plural = "Назначения сотрудников на проекты"

    def __str__(self):
        return f"{self.employee} - {self.project}"
