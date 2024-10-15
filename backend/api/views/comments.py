from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from comments.models import Comment
from api.serializers.comments import CommentSerializer
from api.filters.comments import CommentFilter


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Comment.

    Этот ViewSet предоставляет методы для работы с моделью Comment.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    комментариев.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CommentFilter

    def create(self, request, *args, **kwargs):
        request.data.update({"updated_by": request.user.pk})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update({"updated_by": request.user.pk})
        return super().update(request, *args, **kwargs)
