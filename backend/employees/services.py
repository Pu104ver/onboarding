from employees.models import Employee, CuratorEmployees
from projects.models import Project, ProjectAssignment
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from typing import Optional
from core.utils import check_object_existence
from datetime import datetime
from users.validators import check_valid_email


User = get_user_model()


class EmployeeService:
    @staticmethod
    def create_employee(data: dict) -> tuple[Optional[Employee], Optional[str]]:
        """
        Создает сотрудника на основе переданных данных.
        Обязательные поля: email, full_name, role, telegram_nickname

        Args:
            data (dict): словарь с данными сотрудника

        Returns:
            tuple (Optional[Employee], Optional[str]): созданный сотрудник и сообщение об ошибке (если есть)
        """

        correct, error = EmployeeService.check_required_fields(data)
        if error:
            return None, error

        email: str = data.get("email")
        full_name = data.get("full_name")
        role = data.get("role")
        date_of_employment = data.get("date_of_employment")
        telegram_nickname = data.get("telegram_nickname")
        date_of_dismission = data.get("date_of_dismission")
        telegram_user_id = data.get("telegram_user_id")
        description = data.get("description")
        date_meeting = data.get("date_meeting")
        status = data.get("status", Employee.EmployeeStatus.ONBOARDING)
        risk_status = data.get("risk_status", Employee.RiskStatus.NOPROBLEM)
        is_curator_employee = data.get("is_curator_employee", False)
        is_archived = data.get("is_archived", False)
        created_by = data.get("created_by")
        updated_by = data.get("updated_by")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"email": email},
        )

        correct, error = check_valid_email(email=email)
        if not correct:
            return None, error

        if Employee.objects.filter(user=user).exists():
            return (
                None,
                f"Сотрудник не может быть создан. Пользователь с почтой {email} уже существует.",
            )

        if (
            telegram_user_id is not None
            and Employee.objects.filter(telegram_user_id=telegram_user_id).exists()
        ):
            return (
                None,
                f"Сотрудник не может быть создан. Пользователь с telegram_id {telegram_user_id} уже существует.",
            )

        try:
            if isinstance(date_of_employment, str):
                date_of_employment = datetime.strptime(
                    date_of_employment, "%Y-%m-%d"
                ).date()
        except ValueError:
            return (
                None,
                "Поле даты первого рабочего дня должно быть в формате 'YYYY-MM-DD'.",
            )

        employee = Employee(
            user=user,
            full_name=full_name,
            role=role,
            telegram_nickname=telegram_nickname,
            telegram_user_id=telegram_user_id,
            description=description,
            date_of_employment=date_of_employment,
            date_of_dismission=date_of_dismission,
            date_meeting=date_meeting,
            status=status,
            risk_status=risk_status,
            is_curator_employee=is_curator_employee,
            is_archived=is_archived,
            created_by=created_by,
            updated_by=updated_by,
        )

        employee.save()

        return employee, None

    @staticmethod
    def create_employee_projects_assignment(
        employee: Employee, project_ids: list[int], enable_checks: bool = False
    ) -> tuple[list[ProjectAssignment], Optional[str]]:
        """
        Назначает сотруднику проекты.

        Args:
            employee (Employee): объект сотрудника
            project_ids (list[int]): идентификаторы проектов
            enable_checks (bool, optional): включает проверки для переданных данных. Defaults to False.
        Returns:
            tuple (list[ProjectAssignment], Optional[str]): список назначенных проектов и сообщение об ошибке (если есть)
        """
        if enable_checks:
            success, error = check_object_existence(Project, project_ids)
            if not success:
                return [], "Не удалось назначить проекты. Проекты не существуют."

        projects_assignment: list[ProjectAssignment] = []

        for project_id in project_ids:
            projects_assignment.append(
                ProjectAssignment.objects.create(
                    employee=employee,
                    project_id=project_id,
                )
            )

        return projects_assignment, None

    @staticmethod
    def create_curator_employee_assignment(
        employee: Employee, curator_ids: list[int], enable_checks: bool = False
    ) -> tuple[list[CuratorEmployees], Optional[str]]:
        """
        Назначет кураторов для переданного сотрудника.
        Проверяет чтобы кураторы были кураторами проектов сотрудника.

        Args:
            employee (Employee): объект сотрудника
            curator_ids (list[int]): идентификаторы кураторов
            enable_checks (bool, optional): включает проверки для переданных данных. Defaults to False.
        Returns:
            tuple ([list[CuratorEmployees], Optional[str]]): список назначенных кураторов и сообщение об ошибке (если есть)
        """

        if enable_checks:
            success, error = check_object_existence(
                Employee, [employee.id], role=Employee.RoleChoices.EMPLOYEE
            )
            if not success:
                return [], "Не удалось назначить кураторов. Сотрудник не существует."

            success, error = check_object_existence(
                Employee, curator_ids, role=Employee.RoleChoices.CURATOR
            )
            if not success:
                return [], "Не удалось назначить кураторов. Куратор(-ы) не существуют."

        employee_projects_ids: QuerySet[int] = employee.projects_assigned.values_list(
            "project_id", flat=True
        )

        curators_assigment: list[CuratorEmployees] = []

        for curator_id in curator_ids:
            curator_project_id = ProjectAssignment.objects.filter(
                employee_id=curator_id,
                project_id__in=employee_projects_ids,
            ).values_list("project_id", flat=True)

            if not curator_project_id:
                return [], "Переданные кураторы не привязаны к проектам сотрудника."

            curators_assigment.append(
                CuratorEmployees.objects.create(
                    employee=employee, curator_id=curator_id
                )
            )

        return curators_assigment, None

    @staticmethod
    def update_curator_employee_assignment(
        employee: Employee,
        curator: Employee,
        curator_employee: CuratorEmployees,
        enable_checks: bool = False,
    ) -> tuple[CuratorEmployees, Optional[str]]:
        """
        Назначает кураторов для переданного сотрудника.
        Проверяет чтобы кураторы были кураторами проектов сотрудника.

        Args:
            employee (Employee): объект сотрудника для обновления
            curator_id (Employee): объект куратора для обновления
            curator_employee (CuratorEmployees): объект связи куратора с сотрудником, который будет обновлен
            enable_checks (bool, optional): включает проверки для переданных данных. Defaults to False.
        Returns:
            tuple ([CuratorEmployees, Optional[str]]): обновленная связь куратора-сотрудника и сообщение об ошибке (если есть)
        """
        if enable_checks:
            success, error = check_object_existence(
                Employee, [employee.id], role=Employee.RoleChoices.EMPLOYEE
            )
            if not success:
                return None, "Не удалось назначить кураторов. Сотрудник не существует."

            success, error = check_object_existence(
                Employee, [curator.id], role=Employee.RoleChoices.CURATOR
            )
            if not success:
                return None, "Не удалось назначить кураторов. Куратор не существует."

            success, error = check_object_existence(
                CuratorEmployees, [curator_employee.id]
            )
            if not success:
                return (
                    None,
                    "Не удалось обновить связь куратора с сотрудником. Связь не существует.",
                )

        employee_projects_ids: QuerySet[int] = employee.projects_assigned.values_list(
            "project_id", flat=True
        )
        curator_project_id = ProjectAssignment.objects.filter(
            employee_id=curator.id,
            project_id__in=employee_projects_ids,
        ).values_list("project_id", flat=True)

        if not curator_project_id:
            return None, "Переданные кураторы не привязаны к проектам сотрудника."

        curator_employee.employee = employee
        curator_employee.curator = curator
        curator_employee.save()

        return curator_employee, None

    @staticmethod
    def check_required_fields(data: dict) -> tuple[bool, Optional[str]]:
        """
        Проверяет наличие обязательных полей в переданной структуре данных.

        Args:
            data (dict): структура данных с данными для создания сотрудника

        Returns:
            tuple ([bool, Optional[str]]): результат проверки и сообщение об ошибке (если есть)
        """
        required_fields = [
            "email",
            "full_name",
            "role",
            "telegram_nickname",
        ]
        for field in required_fields:
            if field not in data:
                return None, f"Поле '{field}' обязательно для заполнения."

        return True, None
