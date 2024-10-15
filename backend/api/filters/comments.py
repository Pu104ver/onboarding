import django_filters
from employees.models import Employee
from comments.models import Comment


class CommentFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(), 
        field_name="author", 
        label="Автор комментария"
    )
    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        field_name="employee",
        label="Кому адресован комментарий",
    )
    text = django_filters.CharFilter(
        field_name="text", lookup_expr="icontains", label="Текст комментария"
    )

    class Meta:
        model = Comment
        fields = ["author", "employee", "text"]
