from django.db import models
from django.utils import timezone
from core.managers import SoftDeleteManager


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель, которая добавляет логическое поле для отслеживания удаления объектов.
    Метод delete() переопределен, чтобы отметить объект как удаленный, а не удалить его физически.
    Для физического удаления объекта используйте метод hard_delete().
    
    Attributes:
        is_deleted (BooleanField): Флаг удаления
        deleted_at (DateTimeField): Время удаления
        
    Methods:
    - delete(using=None, keep_parents=False): мягкое удаление
    - hard_delete(using=None, keep_parents=False): физическое удаление
    - restore(): восстановление
    """

    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Время удаления"
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super(SoftDeleteModel, self).delete(using, keep_parents)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()
