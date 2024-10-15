from rest_framework import serializers
from projects.models import Project, ProjectAssignment
from employees.models import Employee
from typing import List, Optional


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    date_start = serializers.DateField(required=False, allow_null=True)
    date_end = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "date_start",
            "date_end",
            "is_deleted",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        extra_kwargs = {
            "is_deleted": {"required": False, "default": False},
            "created_by": {"required": False},
            "created_at": {"required": False},
            "updated_by": {"required": False},
            "updated_at": {"required": False},
        }


class ProjectAssignmentSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=True, write_only=True
    )

    project_details = ProjectSerializer(source="project", read_only=True)

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=True,
        write_only=True,
    )
    from api.serializers.employees import EmployeeBaseSerializer

    employee_details = EmployeeBaseSerializer(source="employee", read_only=True)

    date_of_employment = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = ProjectAssignment
        fields = [
            "id",
            "project",
            "project_details",
            "employee",
            "employee_details",
            "date_of_employment",
        ]


class ProjectAssignmentBulkCreateSerializer(serializers.Serializer):
    projects = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Project.objects.all()),
        write_only=True,
    )
    employees = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all()),
        write_only=True,
    )

    def validate(self, data):
        projects: Optional[List[Project]] = data.get("projects", [])
        employees: Optional[List[Employee]] = data.get("employees", [])

        if not projects or not employees:
            raise serializers.ValidationError(
                "Списки проектов и сотрудников не могут быть пустыми."
            )

        return data
