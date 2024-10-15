from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import CustomUserManager
from django.contrib.auth import get_user_model
from django.utils import timezone


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


class AuthenticationApplication(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=255, blank=True, null=True)
    base_host = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class AuthenticationToken(models.Model):
    profile = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_in = models.DateTimeField()
    application = models.ForeignKey(AuthenticationApplication,
                                    on_delete=models.CASCADE, related_name='application')

    def is_access_token_expired(self):
        return self.expires_in <= timezone.now()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["application", "access_token"],
                name="unique_application_access_token")]
