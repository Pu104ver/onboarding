from users.services.auth.keycloak.config import get_keycloak_client
from users.services.auth.keycloak.services import refresh_keycloak_token
from users.models import AuthenticationToken
from users.exceptions import UserAuthError


def refresh_token(refresh_token):
    token = AuthenticationToken.objects.filter(refresh_token=refresh_token).first()

    if not token:
        raise UserAuthError("Предоставлены неверные данные авторизации")

    match token.application.name:
        case "keycloak":
            return refresh_keycloak_token(token)
        case _:
            raise UserAuthError("Предоставлены неверные данные авторизации")


def _keycloak_logout_session(token):
    keycloak_client = get_keycloak_client()
    return keycloak_client.logout(refresh_token=token)
