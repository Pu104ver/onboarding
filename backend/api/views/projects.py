from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from api.permissions import IsAdminOrHR
from projects.models import Project, ProjectAssignment
from employees.models import Employee
from api.serializers.projects import (
    ProjectSerializer,
    ProjectAssignmentSerializer,
    ProjectAssignmentBulkCreateSerializer,
)
from api.filters.projects import ProjectFilter, ProjectAssignmentFilter
from rest_framework.request import Request
from typing import Any, List
from drf_yasg.utils import swagger_auto_schema


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Project.

    Этот ViewSet предоставляет методы для работы с моделью Project.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    проектов.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter

    def get_permissions(self):
        """
        Получить разрешения для текущей операции.

        Проверяет текущую операцию и устанавливает соответствующие классы разрешений на основе операции.
        Если операция является созданием/редактированием, классы разрешений устанавливаются в [IsAdminOrHR].
        В противном случае, классы разрешений устанавливаются в [IsAuthenticated].

        Возвращает:
            Разрешения для текущей операции.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminOrHR]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer: ProjectSerializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer: ProjectSerializer):
        serializer.save(updated_by=self.request.user)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance: Project = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if "is_deleted" in request.data and request.data["is_deleted"] is False:
            instance.restore()

        self.perform_update(serializer)
        self.perform_update(serializer)
        return Response(serializer.data)


class ProjectAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью ProjectAssignment.

    Этот ViewSet предоставляет методы для работы с моделью ProjectAssignment.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    назначений проектов.
    """

    queryset = ProjectAssignment.objects.all()
    serializer_class = ProjectAssignmentSerializer
    filterset_class = ProjectAssignmentFilter

    def get_permissions(self):
        """
        Получить разрешения для текущей операции.

        Проверяет текущую операцию и устанавливает соответствующие классы разрешений на основе операции.
        Если операция является созданием/редактированием, классы разрешений устанавливаются в [IsAdminOrHR].
        В противном случае, классы разрешений устанавливаются в [IsAuthenticated].

        Возвращает:
            Разрешения для текущей операции.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminOrHR]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class ProjectAssignmentBulkCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ProjectAssignmentBulkCreateSerializer,
        responses={201: ProjectAssignmentSerializer(many=True)},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ProjectAssignmentBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        projects: List[Project] = serializer.validated_data["projects"]
        employees: List[Employee] = serializer.validated_data["employees"]

        created_assignments: List[ProjectAssignment] = []

        for project in projects:
            for employee in employees:
                assignment: ProjectAssignment
                created: bool
                assignment, created = ProjectAssignment.objects.get_or_create(
                    project=project, employee=employee
                )
                if created:
                    created_assignments.append(assignment)

        return Response(
            ProjectAssignmentSerializer(created_assignments, many=True).data,
            status=status.HTTP_201_CREATED,
        )
