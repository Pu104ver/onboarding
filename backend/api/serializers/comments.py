from rest_framework import serializers
from comments.models import Comment
from employees.models import Employee


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=True
    )
    author_fullname = serializers.CharField(source="author.full_name", read_only=True)
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=True
    )
    employee_fullname = serializers.CharField(
        source="employee.full_name", read_only=True
    )
    text = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "author_fullname",
            "employee",
            "employee_fullname",
            "text",
            "created_at",
            "updated_at",
            "updated_by",
        ]

    extra_kwargs = {
        "created_at": {"required": False},
        "updated_at": {"required": False},
        "updated_by": {"required": False},
    }

    def validate(self, data):
        """
        Проверяет что автор комментария и сотрудник не совпадают
        """
        author = data.get("author")
        employee = data.get("employee")
        if author and employee:
            if author == employee:
                raise serializers.ValidationError(
                    "Автор комментария и сотрудник не могут совпадать."
                )
        return data
