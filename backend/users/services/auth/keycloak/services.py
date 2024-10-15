import base64
import logging

from django.utils import timezone

from keycloak.exceptions import KeycloakAuthenticationError

from users.exceptions import UserAuthError
from users.services.auth.keycloak import config
from users.models import CustomUser, AuthenticationToken


log = logging.getLogger(__name__)


def create_keycloak_user(django_user):
    """
    Создает пользователя в Keycloak
    """
    keycloak_admin = config.get_keycloak_admin()
    try:
        data = {
            "username": django_user.email,
            "email": django_user.email,
            "emailVerified": True,
            "enabled": True,
        }

        if django_user.password:
            credentials = [
                {
                    "type": "password",
                    "value": django_user.password,
                    "temporary": False,  # Если True, пользователь должен будет сменить пароль при первом входе
                }
            ]
            data["credentials"] = credentials

        # Создание пользователя в Keycloak
        user_id = keycloak_admin.create_user(data, exist_ok=False)
        return user_id
    except Exception as e:
        log.error("Error creating user in Keycloak: %s", str(e))
        return None


def update_keycloak_user_password(django_user):
    """
    Обновляет пароль пользователя в Keycloak
    """
    keycloak_admin = config.get_keycloak_admin()
    try:
        user_id = keycloak_admin.get_user_id(django_user.email)
        data = {}
        if django_user.password:
            algorithm, iterations, salt, hashed_value = django_user.password.split("$")
            credentials = [
                {
                    "algorithm": algorithm.replace("_", "-"),
                    "type": "password",
                    "hashedSaltedValue": hashed_value,
                    "hashIterations": iterations,
                    "salt": base64.b64encode(salt.encode()).decode("ascii").strip(),
                    "temporary": False,  # Если True, пользователь должен будет сменить пароль при первом входе
                }
            ]
            data["credentials"] = credentials
        # Обновление пользователя в Keycloak
        user_id = keycloak_admin.update_user(user_id=user_id, payload=data)
        return user_id
    except Exception as e:
        log.error("Error updating user in Keycloak: %s", str(e))
        return None


def update_keycloak_user(django_user):
    """
    Обновляет данные пользователя в Keycloak
    """
    keycloak_admin = config.get_keycloak_admin()
    try:
        user_id = keycloak_admin.get_user_id(django_user.email)
        # Обновление пользователя в Keycloak
        user_id = keycloak_admin.update_user(
            user_id=user_id,
            payload={
                "username": django_user.email,
                "email": django_user.email,
            },
        )
        return user_id
    except Exception as e:
        log.error("Error updating user in Keycloak: %s", str(e))
        return None


def update_or_create_auth_token(
    profile: CustomUser, session_id: str, oauth: dict, application: str = "keycloak"
) -> AuthenticationToken:
    """
    Обновляет или создает токен пользователя при авторизации через Keycloak

    Args:
        user (CustomUser): Профиль пользователя
        oauth (dict): Oauth информация
        session_id (str): Идентификатор сессии Oauth
        application (str, optional): Приложение авторизации. Defaults to 'keycloak'.
    """
    expires_in = timezone.now() + timezone.timedelta(seconds=oauth.get('expires_in'))

    token = AuthenticationToken(
        profile=profile,
        session_id=session_id,
        access_token=oauth.get('access_token'),
        refresh_token=oauth.get('refresh_token'),
        expires_in=expires_in,
        application=application
    )

    try:
        auth_token = AuthenticationToken.objects.get(profile=profile,
                                                     application=application)
        auth_token.session_id = session_id
        auth_token.access_token = oauth.get('access_token')
        auth_token.refresh_token = oauth.get('refresh_token')
        auth_token.expires_in = expires_in
        auth_token.save()
        return auth_token
    except AuthenticationToken.DoesNotExist:
        # Токена не существует, создаем
        token.save()
        return token
    except AuthenticationToken.MultipleObjectsReturned:
        # Существует несколько токенов, удаляем и создаем новый
        AuthenticationToken.objects.filter(profile=profile,
                                           application=application).delete()
        token.save()
        return token


def refresh_keycloak_token(old_token: AuthenticationToken) -> AuthenticationToken:
    """Обновляет токен пользователя в Keycloak

    Args:
        token (AuthenticationToken): Токен пользователя

    Raises:
        UserAuthError: Предоставлены неверные данные авторизации

    Returns:
        AuthenticationToken: Новый токен пользователя
    """
    keycloak_client = config.get_keycloak_client()
    new_token = keycloak_client.refresh_token(old_token.refresh_token)

    if not new_token:
        raise UserAuthError(detail="Предоставлены неверные данные авторизации")

    application = old_token.application
    token_data = decode_token(new_token.get("access_token"))
    user = old_token.profile

    return update_or_create_auth_token(
        profile=user,
        oauth=new_token,
        application=application,
        session_id=token_data.get("sid"),
    )


def decode_token(token) -> dict:
    """Декодирует токен пользователя в Keycloak"""
    keycloak_client = config.get_keycloak_client()
    return keycloak_client.decode_token(token)


def keycloak_authenticate(username, password):
    keycloak_client = config.get_keycloak_client()
    try:
        # Аутентификация в Keycloak
        token = keycloak_client.token(username, password)
        return token
    except KeycloakAuthenticationError:
        return None
