import django_filters
from questions.models import (
    PollQuestion,
    TimeOfDay,
    UserType,
    PollType,
    PollStatus,
    UserAnswer,
    Question,
)
from employees.models import Employee
from django.db.models import Count, Q, QuerySet


class PlannedPollsListFilter(django_filters.FilterSet):
    """
    Фильтрсет для модели PollStatus.
    """

    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        label="Сотрудник",
    )

    target_employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(),
        label="Сотрудник, по которому происходит опрос (таргет сотрудник)",
    )

    target_employee_is_null = django_filters.BooleanFilter(
        field_name="target_employee",
        label="Опросы без привязки к таргету (личные опросы сотрудника)",
        lookup_expr="isnull",
    )

    poll_question = django_filters.ModelChoiceFilter(
        queryset=PollQuestion.all_objects.all(),
        label="Шаблон опроса",
        field_name="poll",
    )

    status = django_filters.ChoiceFilter(
        choices=PollStatus.Status.choices,
        label="Статус прохождения опроса",
    )

    title = django_filters.CharFilter(
        field_name="poll__title", lookup_expr="icontains", label="Название опроса"
    )

    message = django_filters.CharFilter(
        field_name="poll__message", lookup_expr="icontains", label="Сообщение"
    )

    days_after_hire = django_filters.NumberFilter(
        field_name="poll__days_after_hire", label="Дни после устройства"
    )

    time_of_day = django_filters.ChoiceFilter(
        field_name="poll__time_of_day",
        choices=TimeOfDay.choices,
        label="Время суток начала опроса",
    )

    intended_for = django_filters.ChoiceFilter(
        field_name="poll__intended_for",
        choices=UserType.choices,
        label="Предназначен для",
    )

    poll_type = django_filters.ChoiceFilter(
        field_name="poll__poll_type",
        choices=PollType.choices,
        label="Тип опроса",
    )

    has_answers = django_filters.BooleanFilter(
        method="filter_has_answers", label="Есть ответы"
    )

    requires_attention = django_filters.BooleanFilter(
        method="filter_requires_attention", label="Ответ требует внимания"
    )

    created_by_admin = django_filters.BooleanFilter(label="Создан администратором")

    is_archived = django_filters.BooleanFilter(label="В архиве")

    show = django_filters.BooleanFilter(
        method="filter_show", label="Содержит 'существенные' вопросы"
    )

    class Meta:
        model = PollStatus
        fields = [
            "employee",
            "target_employee",
            "target_employee_is_null",
            "poll_question",
            "status",
            "title",
            "message",
            "days_after_hire",
            "time_of_day",
            "intended_for",
            "poll_type",
            "has_answers",
            "requires_attention",
            "created_by_admin",
            "is_archived",
            "show",
        ]

    def filter_has_answers(self, queryset: QuerySet, name, value):
        employee_id = self.request.query_params.get("employee")
        target_employee_id = self.request.query_params.get("target_employee")

        if employee_id:
            queryset = queryset.filter(
                poll__questions__useranswer__employee_id=employee_id
            )

        if target_employee_id:
            queryset = queryset.filter(
                poll__questions__useranswer__target_employee_id=target_employee_id
            )

        if value:
            queryset = queryset.annotate(
                answer_count=Count("poll__questions__useranswer")
            ).filter(answer_count__gt=0)
        else:
            queryset = queryset.annotate(
                answer_count=Count("poll__questions__useranswer")
            ).filter(answer_count=0)

        return queryset

    def filter_requires_attention(self, queryset: QuerySet, name, value):
        if value:
            return queryset.filter(poll__questions__useranswer__requires_attention=True)
        else:
            return queryset.filter(
                poll__questions__useranswer__requires_attention=False
            )

    def filter_show(self, queryset: QuerySet, name, value):
        if value:
            return queryset.filter(poll__questions__show=True)
        else:
            return queryset.exclude(poll__questions__show=False)


class AvailablePollQuestionsFilter(django_filters.FilterSet):
    """
    Фильтрсет модели PollQuestion для фильтрации доступных вопросов.
    """

    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(), label="Сотрудник", method="filter_by_employee"
    )
    intended_for = django_filters.ChoiceFilter(
        field_name="intended_for",
        choices=UserType.choices,
        label="Предназначено для",
    )
    poll_type = django_filters.ChoiceFilter(
        field_name="poll_type",
        choices=[
            (choice_value, choice_label)
            for choice_value, choice_label in PollType.choices
            if choice_value != PollType.INTERMEDIATE_FEEDBACK
        ],
        label="Тип опроса",
    )

    class Meta:
        model = PollQuestion
        fields = ["employee", "intended_for", "poll_type"]

    def filter_by_employee(self, queryset: QuerySet, name, employee: Employee):
        if employee:
            queryset = queryset.filter(intended_for=employee.role)
            employee_projects = employee.projects_assigned.all().values_list(
                "project_id", flat=True
            )

            if not employee_projects:
                queryset = queryset.exclude(content_type__model="project")
            else:
                queryset = queryset.exclude(
                    Q(content_type__model="project")
                    & ~Q(object_id__in=employee_projects)
                )

            # Получаем опросы сотрудника, которые были начаты
            employee_not_valid_pollstatuses = employee.employee_pollstatus.exclude(
                status=PollStatus.Status.NOT_STARTED
            ).values_list("poll_id", flat=True)

            # Исключаем опросы сотрудника, которые были начаты
            return queryset.exclude(id__in=employee_not_valid_pollstatuses)

        return queryset


class UserAnswerFilter(django_filters.FilterSet):
    """
    Фильтрсет для модели UserAnswer.
    """

    employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(), label="Сотрудник"
    )
    target_employee = django_filters.ModelChoiceFilter(
        queryset=Employee.objects.all(), label="Сотрудник, по которому был дан ответ"
    )
    question = django_filters.ModelMultipleChoiceFilter(
        queryset=Question.objects.all(), label="Вопрос"
    )
    poll = django_filters.ModelMultipleChoiceFilter(
        queryset=PollQuestion.objects.all(), field_name="question__poll", label="Опрос"
    )
    poll_status = django_filters.ModelMultipleChoiceFilter(
        queryset=PollStatus.objects.all(),
        field_name="employee__employee_pollstatus",
        label="Статус опроса",
    )
    requires_attention = django_filters.BooleanFilter(label="Ответ требует внимания")
    created_at = django_filters.DateTimeFromToRangeFilter(label="Дата ответа")

    class Meta:
        model = UserAnswer
        fields = [
            "employee",
            "target_employee",
            "question",
            "poll",
            "poll_status",
            "requires_attention",
            "created_at",
        ]
