from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from api.serializers.users import AuthenticationSerializer
from drf_yasg.utils import swagger_auto_schema


User = get_user_model()


class CustomAuthToken(ObtainAuthToken):
    """
    View для получения токена авторизации пользователя.

    Метод HTTP POST.

    Принимает в теле запроса email и пароль (в формате JSON).
    Возвращает токен авторизации пользователя (в формате JSON).
    """

    @swagger_auto_schema(
        request_body=AuthenticationSerializer, responses={200: "Token, user_id, email"}
    )
    def post(self, request, *args, **kwargs):
        serializer = AuthenticationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})
