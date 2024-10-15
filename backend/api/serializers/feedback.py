from rest_framework import serializers
from feedback.models import FeedbackUser
from employees.models import Employee
from api.serializers.employees import EmployeeBaseSerializer


class FeedbackUserSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=True
    )
    employee_details = EmployeeBaseSerializer(source="employee", read_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        model = FeedbackUser
        fields = ["id", "employee", "employee_details", "created_at", "text"]
        read_only_fields = ["id", "created_at"]

    extra_kwargs = {
        "created_at": {"required": False},
    }
