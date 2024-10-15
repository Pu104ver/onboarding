from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Модель пользователя.

    Это расширение стандартной модели пользователя Django.

    Attributes:
        email (EmailField): Электронная почта.
        is_staff (BooleanField): Флаг, указывающий, что пользователь является администратором.
        is_active (BooleanField): Флаг, указывающий, что пользователь активен.
        date_joined (DateTimeField): Дата регистрации.
    """

    username = None
    email = models.EmailField(max_length=128, verbose_name="Email", unique=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
