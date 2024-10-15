from rest_framework import serializers
from employees.models import Employee, CuratorEmployees
from django.contrib.auth import get_user_model
from api.serializers.users import UserProfileSerializer
from api.serializers.questions import PollStatusSerializer
from projects.models import Project
from typing import List, Optional


User = get_user_model()


class EmployeeBaseSerializer(serializers.ModelSerializer):
    user_details = UserProfileSerializer(source="user", read_only=True)
    onboarding_status = PollStatusSerializer(read_only=True)

    status_display = serializers.SerializerMethodField(read_only=True)
    risk_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "user_details",
            "full_name",
            "telegram_nickname",
            "role",
            "status",
            "status_display",
            "risk_status",
            "risk_status_display",
            "date_meeting",
            "onboarding_status",
        ]

    def get_status_display(self, obj: Employee) -> str:
        return obj.get_status_display()

    def get_risk_status_display(self, obj: Employee) -> str:
        return obj.get_risk_status_display()


class EmployeeProfileSerializer(serializers.ModelSerializer):

    user = UserProfileSerializer()
    projects = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    risk_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "description",
            "role",
            "full_name",
            "telegram_nickname",
            "date_of_employment",
            "date_of_dismission",
            "projects",
            "status",
            "status_display",
            "risk_status",
            "risk_status_display",
            "date_meeting",
        ]
        depth = 1

    def get_projects(self, obj: Employee) -> List[Project]:
        from api.serializers.projects import ProjectSerializer

        projects_ids = obj.projects_assigned.all().values_list("project_id", flat=True)
        projects = Project.objects.filter(id__in=projects_ids)
        return ProjectSerializer(projects, many=True).data

    def get_status_display(self, obj: Employee) -> str:
        return obj.get_status_display()

    def get_risk_status_display(self, obj: Employee) -> str:
        return obj.get_risk_status_display()


class CuratorEmployeeSerializer(serializers.ModelSerializer):
    curator = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.CURATOR),
        required=True,
        write_only=True,
    )

    curator_details = EmployeeBaseSerializer(source="curator", read_only=True)

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.EMPLOYEE),
        required=True,
        write_only=True,
    )

    employee_details = EmployeeBaseSerializer(source="employee", read_only=True)

    class Meta:
        model = CuratorEmployees
        fields = ["id", "curator", "curator_details", "employee", "employee_details"]


class CuratorEmployeeBulkCreateSerializer(serializers.Serializer):
    curators = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Employee.objects.filter(role=Employee.RoleChoices.CURATOR)
        ),
        write_only=True,
    )
    employees = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Employee.objects.filter(role=Employee.RoleChoices.EMPLOYEE)
        ),
        write_only=True,
    )

    def validate(self, data):
        curators: Optional[List[Employee]] = data.get("curators", [])
        employees: Optional[List[Employee]] = data.get("employees", [])

        if not curators or not employees:
            raise serializers.ValidationError(
                "Списки кураторов и сотрудников не могут быть пустыми."
            )

        return data


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    user_details = UserProfileSerializer(source="user", read_only=True)
    role = serializers.ChoiceField(choices=Employee.RoleChoices.choices, required=True)
    full_name = serializers.CharField(required=True)
    telegram_nickname = serializers.CharField(required=True)
    date_of_employment = serializers.DateField(required=True)
    date_of_dismission = serializers.DateField(required=False, allow_null=True)
    date_meeting = serializers.DateTimeField(required=False, allow_null=True)

    status = serializers.ChoiceField(
        choices=Employee.EmployeeStatus.choices, required=False
    )
    risk_status = serializers.ChoiceField(
        choices=Employee.RiskStatus.choices, required=False
    )
    status_display = serializers.SerializerMethodField(read_only=True)
    risk_status_display = serializers.SerializerMethodField(read_only=True)

    projects_list = serializers.SerializerMethodField(read_only=True)
    curators_list = serializers.SerializerMethodField(read_only=True)
    employees_list = serializers.SerializerMethodField(read_only=True)
    onboarding_status = serializers.SerializerMethodField(read_only=True)
    onboarding_status_display = serializers.SerializerMethodField(read_only=True)

    is_curator_employee = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "user_details",
            "role",
            "full_name",
            "telegram_nickname",
            "telegram_user_id",
            "date_of_employment",
            "date_of_dismission",
            "date_meeting",
            "status",
            "status_display",
            "risk_status",
            "risk_status_display",
            "projects_list",
            "curators_list",
            "employees_list",
            "onboarding_status",
            "onboarding_status_display",
            "is_curator_employee",
            "description",
            "is_archived",
            "is_deleted",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        extra_kwargs = {
            "telegram_user_id": {"required": False},
            "description": {"required": False, "allow_blank": True},
            "is_archived": {"required": False, "default": False},
            "is_deleted": {"required": False, "default": False},
            "created_by": {"required": False},
            "created_at": {"required": False},
            "updated_by": {"required": False},
            "updated_at": {"required": False},
        }

    def get_projects_list(self, obj: Employee):
        from api.serializers.projects import ProjectSerializer

        projects = [assignment.project for assignment in obj.projects_assigned.all()]
        return ProjectSerializer(projects, many=True).data

    def get_curators_list(self, obj: Employee) -> List[EmployeeBaseSerializer]:
        if obj.role == Employee.RoleChoices.EMPLOYEE:
            curators = [assignment.curator for assignment in obj.curators.all()]
            return EmployeeBaseSerializer(curators, many=True).data
        return []

    def get_employees_list(self, obj: Employee) -> List[EmployeeBaseSerializer]:
        if obj.role == Employee.RoleChoices.CURATOR:
            employees = [assignment.employee for assignment in obj.employees.all()]
            return EmployeeBaseSerializer(employees, many=True).data
        return []

    def get_onboarding_status(self, obj: Employee) -> Optional[dict]:
        employee_onboarding_status = obj.onboarding_status
        if employee_onboarding_status is None:
            return None
        return PollStatusSerializer(employee_onboarding_status).data

    def get_onboarding_status_display(self, obj: Employee) -> str:
        return (
            obj.onboarding_status.get_status_display()
            if obj.onboarding_status
            else "Нет статуса"
        )

    def get_status_display(self, obj: Employee):
        return obj.get_status_display()

    def get_risk_status_display(self, obj: Employee):
        return obj.get_risk_status_display()

    def validate(self, data):
        """
        Проверяет данные, полученные в формате словаря, на корректность.
        Проверяется дата трудоустройства и дата увольнения.

        Возвращает:
            dict: Проверенные данные.
        """
        date_of_employment = data.get("date_of_employment")
        date_of_dismission = data.get("date_of_dismission")

        if date_of_employment and date_of_dismission:
            if date_of_dismission < date_of_employment:
                raise serializers.ValidationError(
                    "Дата увольнения не может быть раньше даты трудоустройства."
                )

        return data
