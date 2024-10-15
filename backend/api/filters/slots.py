import django_filters
from employees.models import Employee


class SlotFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        field_name="booked_by",
        label="Сотрудник",
    )
    created_at__gte = django_filters.DateFilter(
        field_name="date", lookup_expr="gte", label="Дата (с)"
    )
    created_at__lte = django_filters.DateFilter(
        field_name="date", lookup_expr="lte", label="Дата (по)"
    )
