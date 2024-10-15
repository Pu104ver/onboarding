from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from employees.models import Employee, CuratorEmployees
from employees.services import EmployeeService
from api.permissions import IsAdminOrHR
from api.serializers.employees import (
    EmployeeSerializer,
    EmployeeProfileSerializer,
    CuratorEmployeeSerializer,
    CuratorEmployeeBulkCreateSerializer,
)
from api.filters.employees import EmployeeFilter, CuratorEmployeesFilter
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import transaction
from users.utils import TokenGenerator
from users.validators import check_valid_email
from typing import Any, List, Optional
from drf_yasg.utils import swagger_auto_schema
from dotenv import load_dotenv

import os


load_dotenv()

BOT_URL = os.getenv("BOT_URL")

User = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Employee.

    Этот ViewSet предоставляет методы для работы с моделью Employee.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    сотрудников.
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter

    def get_queryset(self):
        """
        Получить запрос на выборку.

        Предварительно загружает связанные поля 'curators' и 'projects_assigned'.
        Сортирует сотрудников по времени завершения опроса от позднего к раннему.

        Возвращает QuerySet с предварительно загруженными связанными полями и сортировкой.
        """
        queryset = super().get_queryset()
        queryset = Employee.objects.sort_by_poll_completion(queryset)
        queryset = queryset.prefetch_related("curators", "projects_assigned")

        return queryset

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

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Функция для создания сотрудника с предоставленными данными.
        Создает пользователя и генерирует токен для сотрудника.

        Возвращает ответ с идентификатором сотрудника, UID и токеном.
        """
        # По хорошему стоит вынести логику в сервис...
        with transaction.atomic():
            data: dict = request.data.copy()

            project_ids: List[int] = list(set(data.get("projects", [])))
            curator_ids: List[int] = list(set(data.get("curators", [])))

            if curator_ids:
                if data.get("role") == Employee.RoleChoices.CURATOR:
                    raise ValidationError("Нельзя создать куратора с кураторами")
            data["created_by"] = request.user
            data["updated_by"] = request.user

            # создание пользователя и назначение его в ряды работяг
            employee, error = EmployeeService.create_employee(data=data)

            if error:
                raise ValidationError(error)

            if project_ids:
                # назначение проектов
                _, error = EmployeeService.create_employee_projects_assignment(
                    employee=employee,
                    project_ids=project_ids,
                    enable_checks=True,
                )
                if error:
                    raise ValidationError(error)

            if curator_ids:
                # назначение кураторов
                _, error = EmployeeService.create_curator_employee_assignment(
                    employee=employee,
                    curator_ids=curator_ids,
                    enable_checks=True,
                )
                if error:
                    raise ValidationError(error)

            employee.update_onboarding_status()

            uid: str = urlsafe_base64_encode(force_bytes(employee.user.pk))
            token: str = TokenGenerator().make_token(employee.user)
            join_url = f"{BOT_URL}?start={uid}_{token}"

            response_data: dict = {
                "user_id": employee.user.id,
                "employee_id": employee.id,
                "uid": uid,
                "token": token,
                "join_url": join_url,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Обновляет существующий экземпляр с данными, предоставленными в запросе.

        Возвращает:
            Response: Объект ответа.
        """
        # По хорошему стоит вынести логику в сервис...
        with transaction.atomic():
            data: dict = request.data.copy()

            project_ids: Optional[List[int]] = data.get("projects", None)
            curator_ids: Optional[List[int]] = data.get("curators", None)

            data_employee_role = data.get("role", None)
            data_employee_email = data.get("email", None)

            partial = kwargs.pop("partial", False)

            employee: Employee = self.get_object()

            if (
                (
                    data_employee_role == Employee.RoleChoices.CURATOR
                    or employee.role == Employee.RoleChoices.CURATOR
                )
                and curator_ids
                and data_employee_role != Employee.RoleChoices.EMPLOYEE
            ):
                raise ValidationError(
                    "Нельзя создать куратора с кураторами",
                )

            if "is_deleted" in request.data and request.data["is_deleted"] is False:
                employee.restore()

            if data_employee_email is not None:
                correct, error = check_valid_email(email=data_employee_email)
                if not correct:
                    raise ValidationError(error)
                
                employee_email = User.objects.normalize_email(data_employee_email)
                employee.user.email = employee_email
                employee.user.save()

            if project_ids is not None:
                # если переданы проекты, то очищаем существующие связи (кураторов без проекта быть не может)
                employee.curators.all().delete()
                employee.projects_assigned.all().delete()

                # если переданы непустые проекты, то назначаем
                if len(project_ids) > 0:
                    project_ids = list(set(project_ids))

                    _, error = EmployeeService.create_employee_projects_assignment(
                        employee=employee,
                        project_ids=project_ids,
                    )
                    if error:
                        raise ValidationError(error)

            if curator_ids is not None:
                # если переданы кураторы, то очищаем старое
                curator_ids = list(set(curator_ids))
                employee.curators.all().delete()

                # если переданы непустые кураторы, то назначаем
                if len(curator_ids) > 0:
                    _, error = EmployeeService.create_curator_employee_assignment(
                        employee=employee,
                        curator_ids=curator_ids,
                    )
                    if error:
                        raise ValidationError(error)

            if data.get("role") == Employee.RoleChoices.CURATOR:
                employee.curators.all().delete()

            employee.refresh_from_db()

            serializer = self.get_serializer(employee, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user)
            employee.update_onboarding_status()

            return Response(serializer.data)


class CuratorEmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с данными кураторов сотрудников.

    Этот ViewSet предоставляет методы для работы с моделью CuratorEmployees.
    Он поддерживает CRUD операции (создание, чтение, обновление, удаление)
    назначений кураторов.
    """

    queryset = CuratorEmployees.objects.all()
    serializer_class = CuratorEmployeeSerializer
    filterset_class = CuratorEmployeesFilter

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

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except Exception as e:
            return self.handle_exception(e)

    def perform_create(self, serializer):
        """Создает связь м/у куратором и сотрудником."""

        curator = serializer.validated_data["curator"]
        employee = serializer.validated_data["employee"]

        _, error = EmployeeService.create_curator_employee_assignment(
            employee=employee, curator_ids=[curator.id], enable_checks=True
        )
        if error:
            raise ValidationError(error)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)

        except Exception as e:
            return self.handle_exception(e)

    def perform_update(self, serializer):
        """Обновляет связь м/у куратором и сотрудником."""

        curator = serializer.validated_data.get("curator", None)
        employee = serializer.validated_data.get(
            "employee", serializer.instance.employee
        )
        if curator:
            _, error = EmployeeService.update_curator_employee_assignment(
                employee=employee,
                curator=curator,
                curator_employee=serializer.instance,
                enable_checks=True,
            )
            if error:
                raise ValidationError(error)

        serializer.save()


class CuratorEmployeeBulkCreateAPIView(APIView):
    """
    API представление для множнественного создания связей между кураторами и сотрудниками.

    Возвращает:
        Response: Объект ответа (список созданных связей).
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CuratorEmployeeBulkCreateSerializer,
        responses={201: CuratorEmployeeSerializer(many=True)},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = CuratorEmployeeBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        curators: List[Employee] = serializer.validated_data["curators"]
        employees: List[Employee] = serializer.validated_data["employees"]

        created_links: List[CuratorEmployees] = []

        # для каждого куратора назначаем переданных сотрудников
        for curator in curators:
            for employee in employees:
                curator_employee: CuratorEmployees
                created: bool
                curator_employee, created = CuratorEmployees.objects.get_or_create(
                    curator=curator, employee=employee
                )
                if created:
                    created_links.append(curator_employee)

        return Response(
            CuratorEmployeeSerializer(created_links, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class MeAPIView(APIView):
    """
    API представление для получения данных о пользователе-сотруднике.

    Метод GET возвращает данные о сотруднике, связанном с пользователем, отправившим запрос.

    Возвращает:
        Response: Объект ответа с данными сотрудника или сообщением об ошибке.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            employee: Employee = Employee.objects.get(user=request.user)
            serializer = EmployeeProfileSerializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND
            )


class EmployeeStatusListView(APIView):
    """
    API для получения всех возможных статусов сотрудника.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        statuses = [
            {"value": status.value, "label": status.label}
            for status in Employee.EmployeeStatus
        ]
        return Response(statuses, status=status.HTTP_200_OK)


class EmployeeRiskStatusListView(APIView):
    """
    API для получения всех возможных статусов риска сотрудника.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        statuses = [
            {"value": status.value, "label": status.label}
            for status in Employee.RiskStatus
        ]
        return Response(statuses, status=status.HTTP_200_OK)
