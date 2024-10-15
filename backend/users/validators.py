from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

import re


def check_valid_password(password: str, username: str = None) -> tuple[bool, list[str]]:
    """
    Валидатор пароля.
    """
    error_message = []
    validated = True

    try:
        validate_password(password, user=username)
    except ValidationError as e:
        error_message = list(e.messages)
        validated = False

    return validated, error_message


def check_valid_email(email: str) -> tuple[bool, str]:
    """
    Проверяет корректность электронной почты.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        return (
            False,
            "Почта не соответствует формату. Допустимые символы: буквы (a-z, A-Z), цифры (0-9), символы '.', '_', '%', '+', '-'"
        )

    return True, ""
