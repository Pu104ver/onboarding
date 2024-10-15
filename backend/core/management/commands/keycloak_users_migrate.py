import environ
import time
import base64

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from users.models import CustomUser
from keycloak import KeycloakAdmin

env = environ.Env()


class Command(BaseCommand):
    help = "Миграция пользоватей из django в keycloak"

    def handle(self, *args, **options):
        UserModel = get_user_model()
        users = UserModel.objects.all()
        keycloak_admin = self.get_keycloak_admin()
        for user in users:
            keycloak_user = keycloak_admin.get_user_id(user.email)
            if keycloak_user:
                continue
            self.stdout.write(f"Creating user {user.email} (ID: {user.id}) in Keycloak")
            keycloak_user = self.create_keycloak_user(keycloak_admin, user)
            if keycloak_user:
                self.stdout.write(self.style.SUCCESS(f"User {user.email} successfully created in Keycloak"))
            time.sleep(0.2)
        self.check_users_in_keycloak(keycloak_admin)

    def get_keycloak_admin(self):
        keycloak_admin = KeycloakAdmin(
            server_url=env("KEYCLOAK_BASE_URL", str, ""),
            username=env("KEYCLOAK_ADMIN", str, ""),  # Администратор Keycloak
            password=env("KEYCLOAK_ADMIN_PASSWORD", str, ""),
            realm_name=env("KEYCLOAK_REALM", str, ""),
        )
        return keycloak_admin

    def create_keycloak_user(self, keycloak_admin, django_user: CustomUser):
        try:
            data = {
                "username": django_user.email,
                "email": django_user.email,
                "emailVerified": True,
                "enabled": True,
            }
            
            if django_user.password:
                algorithm, iterations, salt, hashed_value = django_user.password.split(
                    "$"
                )
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

            # Создание пользователя в Keycloak
            user_id = keycloak_admin.create_user(data, exist_ok=False)
            return user_id
        except Exception as e:
            self.stderr.write(f"Error creating user in Keycloak: {str(e)}")
            return None

    def check_users_in_keycloak(self, keycloak_admin):
        try:
            users = keycloak_admin.get_users()
            self.stdout.write("Users in Keycloak:")
            for user in users:
                self.stdout.write(f"- {user['username']} (ID: {user['id']})")
        except Exception as e:
            self.stderr.write(f"Error retrieving users from Keycloak: {str(e)}")