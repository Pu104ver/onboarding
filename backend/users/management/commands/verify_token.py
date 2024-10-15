from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.utils import verify_token

User = get_user_model()


class Command(BaseCommand):
    help = "Verify a token using verify_token function"

    def add_arguments(self, parser):
        parser.add_argument("uid", type=str, help="Base64 encoded user ID")
        parser.add_argument("token", type=str, help="Token to verify")

    def handle(self, *args, **options):
        uid = options["uid"]
        token = options["token"]

        verified_user = verify_token(uid, token)
        if verified_user is not None:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Token verification successful for user {verified_user} (ID: {verified_user.pk})"
                )
            )
        else:
            self.stdout.write(self.style.ERROR("Token verification failed"))
