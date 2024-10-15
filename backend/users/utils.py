from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model


User = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    """
    Генератор токена для пользователя.

    Переопределяет метод _make_hash_value, чтобы добавить в хэш-значение
    информацию о том, активен ли пользователь.
    """

    def _make_hash_value(self, user, timestamp):
        return str(user.is_active) + str(user.pk) + str(timestamp)


def verify_token(uid, token):
    """
    Проверяет токен для заданного идентификатора пользователя.

    Параметры:
        uid (str): Идентификатор пользователя для проверки.
        token (str): Токен для проверки.

    Возвращает:
        User
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and TokenGenerator().check_token(user, token):
        return user
    return None
