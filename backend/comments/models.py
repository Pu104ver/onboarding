from django.db import models
from employees.models import Employee
from django.conf import settings


class Comment(models.Model):
    """
    Модель для комментариев к сотрудникам.

    В таблице комментариев будут храниться данные о комментариях к сотрудникам.
    
    Attributes:
        employee (ForeignKey): сотрудник, к которому написан комментарий (Employee)
        author (ForeignKey): автор комментария (Employee)
        text (TextField): текст комментария
        created_at (DateTimeField): время создания комментария
        updated_by (ForeignKey): пользователь, обновивший комментарий
        updated_at (DateTimeField): время обновления комментария
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Сотрудник",
    )
    author = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="authored_comments",
        verbose_name="Автор",
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_comments",
        on_delete=models.SET_NULL,
        verbose_name="Обновлено пользователем",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    def __str__(self):
        return f"Comment by {self.author} on {self.employee}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
