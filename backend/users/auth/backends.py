from rest_framework import authentication, exceptions

from users.models import AuthenticationToken


class AuthenticationTokenBackend(authentication.BaseAuthentication):
    """
    Авторизация пользователя в API по токену
    """

    keyword = "Bearer"
    model = AuthenticationToken

    def get_model(self):
        if self.model is not None:
            return self.model

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        # Проверяем существование токена пользователя
        try:
            token = model.objects.select_related("profile").get(access_token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(("Неверный токен."))

        if not token.profile.is_active:
            raise exceptions.AuthenticationFailed(
                ("Пользователь неактивен или удален.")
            )

        if token.is_access_token_expired():
            raise exceptions.AuthenticationFailed(("Срок действия токена истек."))

        return (token.profile, token)

    def authenticate_header(self, request):
        return self.keyword
