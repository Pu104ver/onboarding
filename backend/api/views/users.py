from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.serializers.users import (
    CustomUserSerializer,
    AuthenticationApplicationSerializer,
)
from users.models import AuthenticationApplication
from users.utils import encrypt_secret
from api.filters.users import CustomUserFilter


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью CustomUser.

    Этот ViewSet предоставляет методы для работы с моделью CustomUser.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    пользователей.
    """

    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CustomUserFilter


class AuthenticationApplicationCreateAPIView(viewsets.ModelViewSet):
    queryset = AuthenticationApplication.objects.all()
    serializer_class = AuthenticationApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request.data.update(
            {"client_secret": encrypt_secret(request.data.get("client_secret"))}
        )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update(
            {"client_secret": encrypt_secret(request.data.get("client_secret"))}
        )
        return super().update(request, *args, **kwargs)
