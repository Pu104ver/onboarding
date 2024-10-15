from django.db import models
from core.models import SoftDeleteModel
from employees.models import Employee


class FeedbackUser(SoftDeleteModel):
    """
    Модель для хранения обратной связи.

    Attributes:
        employee (ForeignKey): Сотрудник, от кого обратная связь
        created_at (DateTimeField): Дата и время обращения.
        text (TextField): Описание проблемы.
    """

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name="Сотрудник (Автор фидбека)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    text = models.TextField(verbose_name="Описание проблемы")

    class Meta:
        verbose_name = "Фидбек"
        verbose_name_plural = "Фидбеки"

    def __str__(self):
        return f"{self.employee.full_name} - {self.text[:20]+'...' if len(self.text) > 20 else self.text}"
