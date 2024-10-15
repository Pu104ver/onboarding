from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from feedback.models import FeedbackUser
from api.serializers.feedback import FeedbackUserSerializer
from api.filters.feedback import FeedbackUserFilter


class FeedbackUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью FeedbackUser.
    
    Предоставляет методы для работы с моделью FeedbackUser.
    """
    queryset = FeedbackUser.objects.all()
    serializer_class = FeedbackUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = FeedbackUserFilter
