import django_filters
from feedback.models import FeedbackUser
from employees.models import Employee


class FeedbackUserFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        field_name="employee",
        label="Сотрудник (Автор фидбека)",
    )
    text = django_filters.CharFilter(
        field_name="text", lookup_expr="icontains", label="Текст фидбека"
    )
    created_at__gte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Дата обращения (с)"
    )
    created_at__lte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Дата обращения (по)"
    )

    class Meta:
        model = FeedbackUser
        fields = ["employee", "text", "created_at__gte", "created_at__lte"]
