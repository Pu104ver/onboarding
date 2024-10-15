import base64
import hashlib
import logging
import requests

from requests import Response, HTTPError, Timeout, RequestException
from requests.auth import AuthBase

from django.conf import settings
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from cryptography.fernet import Fernet

from users.exceptions import ExternalRequestError


log = logging.getLogger(__name__)

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


def make_request(
        endpoint: str, method: str = 'GET', headers: dict = None,
        params: dict = None, data: dict = None, json: dict = None, files: dict = None, auth: AuthBase = None
) -> Response | None:
    try:
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            auth=auth,
            timeout=(60, 120)
        )
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        error_description = ''
        try:
            error_description = str(http_err.response.json())
        except Exception:
            error_description = str(http_err.response.text) or str(http_err)
        log.error(f'{http_err.request.url}. Request error occurred: {error_description}')
    except Timeout as timeout_err:
        log.error(f'Request timed out: {timeout_err}')
    except RequestException as req_err:
        log.error(f'Request error occurred: {req_err}')
    except Exception as err:
        log.error(f'An error occurred: {err}')

    raise ExternalRequestError('Не удалось получить ответ от сервера. Попробуйте позже.')


def encrypt_secret(data: str) -> str:
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_secret(encrypted_secret: str) -> str:
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_secret.encode())
    return decrypted_data.decode()


def get_lower_case_email(email: str) -> str:
    return email.strip().lower()
