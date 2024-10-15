from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.serializers.users import CustomUserSerializer
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
