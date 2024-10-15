from django.db import models

from core.models import SoftDeleteModel
from employees.models import Employee


class Slot(SoftDeleteModel):
    start_time = models.CharField(verbose_name="Время начала")
    date = models.DateField(verbose_name="Дата")
    booked_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Забронирован сотрудником",
    )

    class Meta:
        unique_together = ('start_time', 'date')
        verbose_name = "Слот"
        verbose_name_plural = "Слоты"

    def is_available(self):
        return not self.booked_by
