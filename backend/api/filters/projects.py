import django_filters
from projects.models import Project, ProjectAssignment
from employees.models import Employee


class ProjectFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        field_name="employees",
        label="Сотрудник проекта",
        method="filter_by_employee",
    )

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Название проекта"
    )

    date_start = django_filters.DateFromToRangeFilter(
        field_name="date_start", label="Дата начала проекта"
    )

    date_end = django_filters.DateFromToRangeFilter(
        field_name="date_end", label="Дата окончания проекта"
    )

    class Meta:
        model = Project
        fields = ["name", "date_start", "date_end", "employee"]

    def filter_by_employee(self, queryset, name, value):
        return queryset.filter(employees=value)


class ProjectAssignmentFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(), label="Сотрудник"
    )
    project = django_filters.ModelChoiceFilter(
        queryset=Project.objects.all(), label="Проект"
    )
    date_of_employment = django_filters.DateFilter(
        field_name="date_of_employment",
        lookup_expr="exact",
        label="Дата первого рабочего дня на проекте",
    )
    date_of_employment__gte = django_filters.DateFilter(
        field_name="date_of_employment",
        lookup_expr="gte",
        label="Дата первого рабочего дня (с)",
    )
    date_of_employment__lte = django_filters.DateFilter(
        field_name="date_of_employment",
        lookup_expr="lte",
        label="Дата первого рабочего дня (по)",
    )

    class Meta:
        model = ProjectAssignment
        fields = [
            "employee",
            "project",
            "date_of_employment",
            "date_of_employment__gte",
            "date_of_employment__lte",
        ]
