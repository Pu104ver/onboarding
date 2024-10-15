import django_filters
from employees.models import Employee, CuratorEmployees
from projects.models import Project
from questions.models import PollStatus
from django.db.models import Q, QuerySet
import json


class EmployeeFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(label="Пользователь", method="filter_by_user")
    full_name = django_filters.CharFilter(
        field_name="full_name", lookup_expr="icontains", label="ФИО"
    )
    telegram_nickname = django_filters.CharFilter(
        field_name="telegram_nickname",
        lookup_expr="icontains",
        label="Телеграм никнейм",
    )
    role = django_filters.ChoiceFilter(
        field_name="role",
        choices=Employee.RoleChoices.choices,
        label="Роль",
        method="filter_by_role",
    )
    status = django_filters.ChoiceFilter(
        field_name="status", choices=Employee.EmployeeStatus.choices, label="Статус"
    )
    risk_status = django_filters.ChoiceFilter(
        field_name="risk_status",
        choices=Employee.RiskStatus.choices,
        label="Статус риска",
    )
    has_onboarding_status = django_filters.BooleanFilter(
        field_name="onboarding_status",
        label="Есть опросы",
        method="filter_employees_with_onboarding_status",
    )
    poll_status = django_filters.ChoiceFilter(
        choices=[*PollStatus.Status.choices, ("none", "Нет статуса")],
        method="filter_poll_status",
        label="Статус опроса",
    )
    is_archived = django_filters.BooleanFilter(
        field_name="is_archived", lookup_expr="exact", label="Архивирован"
    )
    date_of_employment__gte = django_filters.DateFilter(
        field_name="date_of_employment", lookup_expr="gte", label="Дата приёма (с)"
    )
    date_of_employment__lte = django_filters.DateFilter(
        field_name="date_of_employment", lookup_expr="lte", label="Дата приёма (по)"
    )
    date_of_dismission__gte = django_filters.DateFilter(
        field_name="date_of_dismission", lookup_expr="gte", label="Дата увольнения (с)"
    )
    date_of_dismission__lte = django_filters.DateFilter(
        field_name="date_of_dismission", lookup_expr="lte", label="Дата увольнения (по)"
    )
    projects = django_filters.CharFilter(
        label="Проекты",
        method="filter_projects",
    )
    curators = django_filters.CharFilter(
        label="Кураторы",
        method="filter_by_curators",
    )
    employees_with_subordinates = django_filters.BooleanFilter(
        method="filter_employees_with_subordinates",
        label="Работяги с подчиненными",
    )
    curators_by_projects = django_filters.CharFilter(
        method="filter_curators_by_projects",
        label="Кураторы по переданным проектам",
    )
    is_curator_employee = django_filters.BooleanFilter(
        method="filter_is_curator_employee",
        label="Сотрудник-куратор",
    )
    show = django_filters.BooleanFilter(
        field_name="employee_useranswer__question__show",
        label="Содержит 'существенные' вопросы",
    )

    class Meta:
        model = Employee
        fields = [
            "user",
            "full_name",
            "telegram_nickname",
            "role",
            "status",
            "risk_status",
            "has_onboarding_status",
            "poll_status",
            "date_of_employment__gte",
            "date_of_employment__lte",
            "date_of_dismission__gte",
            "date_of_dismission__lte",
            "is_archived",
            "projects",
            "curators",
            "employees_with_subordinates",
            "curators_by_projects",
            "is_curator_employee",
            "show",
        ]

    def filter_by_role(self, queryset, name, value):
        """
        Фильтрация сотрудников по роли с учетом флага is_curator_employee.
        """
        if value == Employee.RoleChoices.EMPLOYEE:
            return queryset.filter(
                Q(role=Employee.RoleChoices.EMPLOYEE) | Q(is_curator_employee=True)
            )

        elif value == Employee.RoleChoices.CURATOR:
            return queryset.filter(
                Q(role=Employee.RoleChoices.CURATOR) | Q(is_curator_employee=True)
            )

        return queryset.filter(role=value)

    def filter_by_user(self, queryset: QuerySet, name, user_ids: str):
        if user_ids:
            try:
                user_list = json.loads(user_ids)
            except json.JSONDecodeError:
                return queryset.none()

            queryset = queryset.filter(user__id__in=user_list)

        return queryset

    def filter_projects(self, queryset: QuerySet, name, project_ids: str):
        if project_ids:
            try:
                project_list = json.loads(project_ids)
            except json.JSONDecodeError:
                return queryset.none()

            queryset = queryset.filter(projects_assigned__project__id__in=project_list)

        return queryset

    def filter_by_curators(self, queryset: QuerySet, name, curators_ids: str):
        if curators_ids:
            try:
                curators_list = json.loads(curators_ids)
            except json.JSONDecodeError:
                return queryset.none()

            queryset = queryset.filter(curators__curator__id__in=curators_list)

        return queryset

    def filter_employees_with_onboarding_status(self, queryset: QuerySet, name, value):
        if value:
            return queryset.exclude(onboarding_status__isnull=True)
        else:
            return queryset.exclude(onboarding_status__isnull=False)

    def filter_poll_status(self, queryset: QuerySet, name, value):
        if value == "none":
            return queryset.filter(onboarding_status__isnull=True)

        if value:
            return queryset.filter(
                id__in=[
                    employee.id
                    for employee in queryset
                    if employee.onboarding_status
                    and employee.onboarding_status.status == value
                ]
            )
        return queryset

    def filter_curators_by_projects(self, queryset: QuerySet, name, projects_ids: str):
        if projects_ids:
            try:
                projects_ids_list = json.loads(projects_ids)
            except json.JSONDecodeError:
                return queryset.none()
            projects_ids = Project.objects.filter(id__in=projects_ids_list).values_list(
                "id", flat=True
            )
            return Employee.objects.curators_for_projects(projects_ids)
        return queryset

    def filter_employees_with_subordinates(self, queryset: QuerySet, name, value):
        """
        Фильтр для получения списка сотрудников, которые имеют закрепленных сотрудников.
        """
        if value:
            return queryset.filter(employees__isnull=False)
        else:
            return queryset.filter(employees__isnull=True)

    def filter_is_curator_employee(self, queryset: QuerySet, name, value):
        if value:
            role = self.request.query_params.get("role")
            queryset = queryset.filter(is_curator_employee=True)
        return queryset


class CuratorEmployeesFilter(django_filters.FilterSet):
    curator = django_filters.CharFilter(
        label="Куратор",
        method="filter_by_curator",
    )
    employee = django_filters.CharFilter(
        label="Сотрудник",
        method="filter_by_employee",
    )

    class Meta:
        model = CuratorEmployees
        fields = ["curator", "employee"]

    def filter_by_curator(self, queryset: QuerySet, name, curator_ids: str):
        if curator_ids:
            try:
                curator_list = json.loads(curator_ids)
            except json.JSONDecodeError:
                return queryset.none()

            queryset = queryset.filter(curator__id__in=curator_list)

        return queryset

    def filter_by_employee(self, queryset: QuerySet, name, employee_ids: str):
        if employee_ids:
            try:
                employee_list = json.loads(employee_ids)
            except json.JSONDecodeError:
                return queryset.none()

            queryset = queryset.filter(employee__id__in=employee_list)

        return queryset
