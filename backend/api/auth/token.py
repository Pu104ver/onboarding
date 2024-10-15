import logging

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.exceptions import UserAuthError
from users.utils import get_lower_case_email
from users.models import AuthenticationApplication, AuthenticationToken
from users.services.token import refresh_token as user_refresh_token

import users.services.auth.keycloak.services as keycloak_service

from api.serializers.users import (
    AuthenticationSerializer,
    UserProfileSerializer,
    ProfileAuthenticationSerializer,
)


log = logging.getLogger(__name__)


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


class KeycloakAuthTokenView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []  # Отключение аутентификации для этого представления

    @swagger_auto_schema(
        request_body=ProfileAuthenticationSerializer,
        resonses={200: UserProfileSerializer},
    )
    def post(self, request):
        auth_serializer = ProfileAuthenticationSerializer(data=request.data)
        auth_serializer.is_valid(raise_exception=True)

        email = get_lower_case_email(
            email=auth_serializer.validated_data.get("email", "")
        )
        password = auth_serializer.validated_data.get("password")

        # Аутентификация через Keycloak
        keycloak_token = keycloak_service.keycloak_authenticate(email, password)
        if keycloak_token:
            # Ищем пользователя в БД
            user = User.objects.filter(email=email).first()

            application = AuthenticationApplication.objects.filter(
                name="keycloak"
            ).first()

            token_data = keycloak_service.decode_token(
                keycloak_token.get("access_token")
            )

            keycloak_service.update_or_create_auth_token(
                profile=user,
                session_id=token_data.get("sid"),
                oauth=keycloak_token,
                application=application,
            )

            log.info(msg=f"Пользователь {user.email} успешно авторизован")

            # Сериализуем данные пользователя
            profile_serialized = UserProfileSerializer(instance=user)
            # Если аутентификация успешна, возвращаем токен Keycloak
            return Response(
                {
                    "access_token": keycloak_token.get("access_token"),
                    "refresh_token": keycloak_token.get("refresh_token"),
                    "expires_in": keycloak_token.get("expires_in"),
                    "user": profile_serialized.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            raise AuthenticationFailed(
                detail="Предоставлены неверные данные авторизации"
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Отключение аутентификации для этого представления

    @swagger_auto_schema(
        operation_description="Обновление access и refresh токенов с помощью refresh токена.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh token",
                    example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                )
            },
            required=["refresh_token"],
        ),
        responses={
            200: openapi.Response(
                description="Токены успешно обновлены",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access_token": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Access token"
                        ),
                        "refresh_token": openapi.Schema(
                            type=openapi.TYPE_STRING, description="New Refresh token"
                        ),
                        "expires_in": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Время жизни access token в секундах",
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="ID пользователя",
                                ),
                                "email": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Email пользователя",
                                ),
                                "full_name": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Полное имя пользователя",
                                ),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Некорректный запрос"),
            401: openapi.Response(description="Неверные данные авторизации"),
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            try:
                token = user_refresh_token(refresh_token)
            except UserAuthError:
                raise AuthenticationFailed(
                    detail="Предоставлены неверные данные авторизации"
                )

            user = UserProfileSerializer(instance=token.profile)

            if not token:
                raise AuthenticationFailed(
                    detail="Предоставлены неверные данные авторизации."
                )

            return Response(
                {
                    "access_token": token.access_token,
                    "refresh_token": token.refresh_token,
                    "expires_in": token.expires_in,
                    "user": user.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            raise AuthenticationFailed(
                detail="Предоставлены неверные данные авторизации"
            )


@api_view(['POST'])
@permission_classes(())
def keycloak_callback_signout(request, *args, **kwargs) -> Response | None:
    """
    Обработчик callback для выхода из учетной записи в Keycloak
    """
    token = keycloak_service.decode_token(request.data.get('logout_token'))
    log.info(f"callback от Keycloak, {token.get('sid')} удаляем сессию")
    if token:
        AuthenticationToken.objects.filter(session_id=token.get('sid')).delete()
        return Response(status=200)
