from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для создания пользователей.
    """

    @classmethod
    def normalize_email(cls, email: str):
        """
        Нормализует электронную почту, приводя всю строку к нижнему регистру.
        """
        return email.strip().lower()

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и возвращает пользователя с электронной почтой и паролем.
        """
        if not email:
            raise ValueError("Электронная почта должна быть указана")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и возвращает суперпользователя с электронной почтой и паролем.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
