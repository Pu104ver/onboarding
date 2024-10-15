import environ

from keycloak import KeycloakOpenID

from keycloak import KeycloakAdmin

from users import utils
from users.models import AuthenticationApplication

env = environ.Env()


def get_keycloak_client() -> KeycloakOpenID:
    application = AuthenticationApplication.objects.get(name='keycloak')
    client_secret = utils.decrypt_secret(application.client_secret)
    # Инициализация Keycloak
    keycloak_openid = KeycloakOpenID(
        server_url=env("KEYCLOAK_BASE_URL", str, ""),
        realm_name=env("KEYCLOAK_REALM", str, ""),
        client_id=application.client_id,
        client_secret_key=client_secret
    )
    return keycloak_openid


def get_keycloak_admin():
    keycloak_admin = KeycloakAdmin(
        server_url=env("KEYCLOAK_BASE_URL", str, ""),
        username=env("KEYCLOAK_ADMIN", str, ""),  # Администратор Keycloak
        password=env("KEYCLOAK_ADMIN_PASSWORD", str, ""),
        realm_name=env("KEYCLOAK_REALM", str, ""),
        client_id="admin-cli"
    )
    return keycloak_admin
