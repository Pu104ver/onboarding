from rest_framework import serializers
from employees.models import Employee
from projects.models import Project
from typing import Optional


class InAnalyticsEmployeesSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных статистики по сотрудникам"""
    
    employees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.EMPLOYEE),
        many=True,
        required=True,
    )
    projects = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), many=True, required=False
    )
    curators = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.CURATOR),
        many=True,
        required=False,
    )
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)
    employee_status = serializers.ChoiceField(
        choices=Employee.EmployeeStatus.choices, required=False
    )

    class Meta:
        model = Employee
        fields = [
            "employees",
            "projects",
            "curators",
            "date_start",
            "date_end",
            "employee_status",
        ]


class AnalyticsEmployeesBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    curators = serializers.SerializerMethodField(read_only=True)
    projects = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "status",
            "curators",
            "projects",
        ]

    def __init__(self, *args, **kwargs):
        # Из вью будет приходить статистика по сотрудникам
        self.employees_statistics: dict[int, dict[str, Optional[float]]] = kwargs.pop(
            "employees_statistics", {}
        )
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        employee_statistics: dict[str, Optional[float]] = self.employees_statistics.get(
            instance.id
        )
        representation["employee_statistics"] = employee_statistics

        return representation

    def get_status(self, employee: Employee):
        return employee.get_status_display()

    def get_curators(self, employee: Employee):
        if employee.curators.exists():
            return [
                {curator_employee.curator_id: curator_employee.curator.full_name}
                for curator_employee in employee.curators.all()
            ]

        else:
            return []

    def get_projects(self, employee: Employee):
        if employee.projects_assigned.exists():
            return [
                {project_assigned.project_id: project_assigned.project.name}
                for project_assigned in employee.projects_assigned.all()
            ]

        else:
            return []


class EmployeeAnswersAnalyticsSerializer(AnalyticsEmployeesBaseSerializer):
    general_health = serializers.FloatField(read_only=True)
    responsibilities = serializers.FloatField(read_only=True)
    job_expectations = serializers.FloatField(read_only=True)
    team_satisfactions = serializers.FloatField(read_only=True)
    onboarding_satisfactions = serializers.FloatField(read_only=True)
    interest_project = serializers.FloatField(read_only=True)
    quality_feedback = serializers.FloatField(read_only=True)
    project_expectations = serializers.FloatField(read_only=True)
    understand_tasks_deadlines = serializers.FloatField(read_only=True)

    class Meta(AnalyticsEmployeesBaseSerializer.Meta):
        fields = AnalyticsEmployeesBaseSerializer.Meta.fields + [
            "general_health",
            "responsibilities",
            "job_expectations",
            "team_satisfactions",
            "onboarding_satisfactions",
            "interest_project",
            "quality_feedback",
            "project_expectations",
            "understand_tasks_deadlines",
        ]


class CuratorAnswersAnalyticsSerializer(AnalyticsEmployeesBaseSerializer):
    discipline = serializers.FloatField(read_only=True)
    quality_tasks = serializers.FloatField(read_only=True)
    quality_interactions = serializers.FloatField(read_only=True)
    involvement = serializers.FloatField(read_only=True)
    answer_speed = serializers.FloatField(read_only=True)
    presence_meeting = serializers.FloatField(read_only=True)

    class Meta(AnalyticsEmployeesBaseSerializer.Meta):
        fields = AnalyticsEmployeesBaseSerializer.Meta.fields + [
            "discipline",
            "quality_tasks",
            "quality_interactions",
            "involvement",
            "answer_speed",
            "presence_meeting",
        ]


class InAnalyticsProjectsSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных статистики по проектам"""
    
    projects = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), many=True, required=True
    )
    employees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.EMPLOYEE),
        many=True,
        required=False,
    )
    curators = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(role=Employee.RoleChoices.CURATOR),
        many=True,
        required=False,
    )
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)
    employee_status = serializers.ChoiceField(
        choices=Employee.EmployeeStatus.choices, required=False
    )

    class Meta:
        model = Project
        fields = [
            "projects",
            "employees",
            "curators",
            "date_start",
            "date_end",
            "employee_status",
        ]


class AnalyticsProjectsBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
        ]

    def __init__(self, *args, **kwargs):
        # Из вью будет приходить статистика по проектам
        self.projects_statistics: dict[int, dict[str, Optional[float]]] = kwargs.pop(
            "projects_statistics", {}
        )
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        project_statistics: dict[str, Optional[float]] = self.projects_statistics.get(
            instance.id
        )
        representation["project_statistics"] = project_statistics

        return representation


class AnalyticsProjectsEmployeesSelfAnswersSerializer(AnalyticsProjectsBaseSerializer):
    general_health = serializers.FloatField(read_only=True)
    responsibilities = serializers.FloatField(read_only=True)
    job_expectations = serializers.FloatField(read_only=True)
    team_satisfactions = serializers.FloatField(read_only=True)
    onboarding_satisfactions = serializers.FloatField(read_only=True)
    interest_project = serializers.FloatField(read_only=True)
    quality_feedback = serializers.FloatField(read_only=True)
    project_expectations = serializers.FloatField(read_only=True)
    understand_tasks_deadlines = serializers.FloatField(read_only=True)

    class Meta(AnalyticsProjectsBaseSerializer.Meta):
        fields = AnalyticsProjectsBaseSerializer.Meta.fields + [
            "general_health",
            "responsibilities",
            "job_expectations",
            "team_satisfactions",
            "onboarding_satisfactions",
            "interest_project",
            "quality_feedback",
            "project_expectations",
            "understand_tasks_deadlines",
        ]


class AnalyticsProjectsCuratorsAnswersSerializer(AnalyticsProjectsBaseSerializer):
    discipline = serializers.FloatField(read_only=True)
    quality_tasks = serializers.FloatField(read_only=True)
    quality_interactions = serializers.FloatField(read_only=True)
    involvement = serializers.FloatField(read_only=True)
    answer_speed = serializers.FloatField(read_only=True)
    presence_meeting = serializers.FloatField(read_only=True)

    class Meta(AnalyticsProjectsBaseSerializer.Meta):
        fields = AnalyticsProjectsBaseSerializer.Meta.fields + [
            "discipline",
            "quality_tasks",
            "quality_interactions",
            "involvement",
            "answer_speed",
            "presence_meeting",
        ]
