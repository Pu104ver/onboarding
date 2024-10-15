import django_filters
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class CustomUserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(
        field_name="email", lookup_expr="icontains", label="Электронная почта"
    )
    is_staff = django_filters.BooleanFilter(
        field_name="is_staff", label="Администратор"
    )
    is_active = django_filters.BooleanFilter(field_name="is_active", label="Активен")
    date_joined = django_filters.DateFromToRangeFilter(
        field_name="date_joined", label="Дата регистрации"
    )

    class Meta:
        model = CustomUser
        fields = ["email", "is_staff", "is_active", "date_joined"]
