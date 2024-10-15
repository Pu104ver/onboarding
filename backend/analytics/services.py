from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.db.models import Count, Sum, FloatField, Model
from django.db.models.functions import Cast
from questions.models import (
    UserAnswer,
    QuestionType,
    EmployeeCategoryAnalytics,
    CuratorCategoryAnalytics,
)
from employees.models import Employee
from projects.models import Project
from datetime import datetime, timedelta
from typing import Optional


EMPLOYEE_CATEGORIES = EmployeeCategoryAnalytics

CURATOR_CATEGORIES = CuratorCategoryAnalytics


def calculate_employee_statistics(
    data: dict[str, any],
    curator_answers: bool = False,
) -> tuple[QuerySet[Employee], dict[int, Optional[dict[str, float]]], Optional[str]]:
    """
    Вычисляет статистику по сотрудникам.

    :param dict data: данные для вычисления статистики
    :param bool, optional curator_answers: флаг для вычисления статистики по ответам кураторов, по умолчанию False
    """

    if not data:
        return None, None, None

    employees: QuerySet[Employee] = get_employees_queryset(data.get("employees"))
    curators: Optional[list[Employee]] = data.get("curators")
    projects: Optional[list[Project]] = data.get("projects")
    date_start: Optional[datetime] = data.get("date_start")
    date_end: Optional[datetime] = data.get("date_end")
    employee_status: str = data.get("employee_status")

    employees, error = filter_employees(
        employees=employees,
        projects=projects,
        curators=curators,
        date_start=date_start,
        date_end=date_end,
        employee_status=employee_status,
    )

    if error:
        return None, None, error

    # Фильтры для UserAnswer. Нужны для корректного вычисления статистики. Реализованы здесь, чтобы не таскать фильтры через 100500 методов
    user_answers_filters: list[tuple[UserAnswer, dict[str, any]]] = (
        build_user_answers_filters(date_start=date_start, date_end=date_end)
    )

    employees_statistics = {}

    for employee in employees:
        points, error = average_employee_points_by_categories(
            employee, curator_answers=curator_answers, filters=user_answers_filters
        )

        if error:
            return None, None, error

        employees_statistics[employee.id] = points

    return employees, employees_statistics, None


def calculate_project_statistics(
    data: dict[str, any],
    curator_answers: bool = False,
) -> tuple[QuerySet[Project], dict[int, dict[str, float]] | None, str | None]:
    """
    Вычисляет статистику по проектам.

    :param dict data: данные для вычисления статистики
    :param bool, optional curator_answers: флаг для вычисления статистики по ответам кураторов, по умолчанию False
    """

    if not data:
        return None, None, None

    projects: QuerySet[Project] = get_projects_queryset(data.get("projects"))
    employees: Optional[list[Employee]] = data.get("employees")
    curators: Optional[list[Employee]] = data.get("curators")
    date_start: Optional[datetime] = data.get("date_start")
    date_end: Optional[datetime] = data.get("date_end")
    employee_status: str = data.get("employee_status")
    projects, error = filter_projects(
        projects=projects,
        employees=employees,
        curators=curators,
        date_start=date_start,
        date_end=date_end,
        employee_status=employee_status,
    )

    if error:
        return None, None, error

    # Фильтры для UserAnswer. Нужны для корректного вычисления статистики. Реализованы здесь, чтобы не таскать фильтры через 100500 методов
    user_answers_filters: list[tuple[UserAnswer, dict[str, any]]] = (
        build_user_answers_filters(date_start=date_start, date_end=date_end)
    )

    projects_statistics = {}

    for project in projects:
        points, error = average_project_points_by_categories(
            project, curator_answers=curator_answers, filters=user_answers_filters
        )

        if error:
            return None, None, error

        projects_statistics[project.id] = points

    return projects, projects_statistics, None


def get_employees_queryset(
    employees: list[Employee],
) -> QuerySet[Employee]:
    """
    Возвращает QuerySet сотрудников. Если список сотрудников не передан, то возвращаются все сотрудники.
    """

    if not employees:
        employees = Employee.objects.filter(
            role=Employee.RoleChoices.EMPLOYEE
        ).prefetch_related("employee_useranswer", "projects_assigned", "curators")
    else:
        employees = Employee.objects.filter(
            id__in=[employee.id for employee in employees]
        ).prefetch_related("employee_useranswer", "projects_assigned", "curators")
    return employees


def get_projects_queryset(projects: list[Project]) -> QuerySet[Project]:
    """
    Возвращает QuerySet проектов. Если список проектов не передан, то возвращаются все проекты.
    """

    if not projects:
        projects = Project.objects.all().prefetch_related("employees_assigned")
    else:
        projects = (
            Project.objects.filter(id__in=[project.id for project in projects])
            .distinct()
            .prefetch_related("employees_assigned")
        )
    return projects


def average_employee_points_by_categories(
    employee: Employee,
    categories: list[EmployeeCategoryAnalytics | CuratorCategoryAnalytics] = None,
    curator_answers: bool = False,
    filters: tuple[Model, dict[str, any]] = None,
) -> tuple[Optional[list[dict]], Optional[str]]:
    """
    Принимает сотрудника, список категорий и флаг типа ответов.
    Высчитывает среднее значение оценочных баллов ответов сотрудника по категории.

    Возвращает кортеж ({категория: среднее значение оценочных баллов}, сообщение об ошибке).
    В случае ошибки возвращает кортеж: None и сообщение об ошибке.

    Args:
        employee (Employee): Сотрудник.
        categories (list[CategoryAnalytics]): Список категорий. По умолчанию - все категории.
        curator_answers (Optional[bool]): Флаг типа ответов. Если True - поиск ответов кураторов по переданному сотруднику. Если False - поиск ответов сотрудника. Defaults to False.
        filters (Optional[tuple[Model, dict[str, any]]]): Фильтры (пока что используется лишь для UserAnswer при поиске ответов). Defaults to None.

    Returns:
        Котреж (tuple[Optional[list[dict]]], Optional[str]]): Кортеж средних оценочных баллов по категориям и ошибку.
    """

    if curator_answers:
        categories = categories or CURATOR_CATEGORIES
    else:
        categories = categories or EMPLOYEE_CATEGORIES

    if not employee:
        return None, "Сотрудник не может быть пустым."

    employee_stats = []

    # Распарсинг фильтров
    user_answers_filters: dict[str, any] = {
        filter_field: value
        for model, filter_dict in filters
        if model == UserAnswer
        for filter_field, value in filter_dict.items()
    }

    for category in categories:
        user_answers: QuerySet[UserAnswer] = UserAnswer.objects.select_related(
            "question"
        ).filter(
            question__category_analytics=category,
            question__question_type=QuestionType.NUMBERS,
            **user_answers_filters,
        )

        if curator_answers:
            user_answers = user_answers.filter(target_employee=employee)
        else:
            user_answers = user_answers.filter(employee=employee, target_employee=None)

        # если нет ответов, то пропускаем категорию
        if not user_answers:
            employee_stats.append(
                {
                    "category": category.value,
                    "category_display": category.label,
                    "average": None,
                }
            )
            continue

        user_answers_aggregate: dict = user_answers.annotate(
            answer_as_float=Cast("answer", FloatField())
        ).aggregate(
            total_score=Sum("answer_as_float"),
            total_count=Count("id"),
        )

        total_score: int = user_answers_aggregate.get("total_score", 0)
        total_count: int = user_answers_aggregate.get("total_count", 0)

        if total_count == 0:
            employee_stats.append(
                {
                    "category": category.value,
                    "category_display": category.label,
                    "average": None,
                }
            )
            continue

        average = round(total_score / total_count, 2)

        employee_stats.append(
            {
                "category": category.value,
                "category_display": category.label,
                "average": average,
            }
        )

    return employee_stats, None


def average_project_points_by_categories(
    project: Project,
    categories: list[EmployeeCategoryAnalytics | CuratorCategoryAnalytics] = None,
    curator_answers: bool = False,
    filters: tuple[Model, dict[str, any]] = None,
) -> tuple[Optional[list[dict]], Optional[str]]:
    """
    Принимает проект, список категорий и флаг типа ответов.
    Высчитывает среднее значение оценочных баллов ответов сотрудников проекта по категории.

    Возвращает кортеж ({категория: среднее значение оценочных баллов}, сообщение об ошибке).
    В случае ошибки возвращает кортеж: None и сообщение об ошибке.

    Args:
        project (Project): Проект.
        categories (Optional[list[CategoryAnalytics]]): Список категорий. По умолчанию - все категории. Defaults to None.
        curator_answers (Optional[bool]): Флаг типа ответов. Если True - поиск ответов кураторов по переданному сотруднику. Если False - поиск ответов сотрудника. Defaults to False.
        filters (Optional[tuple[Model, dict[str, any]]]): Фильтры (пока что используется лишь для UserAnswer при поиске ответов). Defaults to None.

    Returns:
        Котреж (tuple[Optional[list[dict]]], Optional[str]]): Кортеж средних оценочных баллов по категориям и ошибка.
    """
    if curator_answers:
        categories = categories or CURATOR_CATEGORIES
    else:
        categories = categories or EMPLOYEE_CATEGORIES

    if not project:
        return None, "Проект не может быть пустым."

    project_stats = []

    # Распарсинг фильтров
    user_answers_filters: dict[str, any] = {
        filter_field: value
        for model, filter_dict in filters
        if model == UserAnswer
        for filter_field, value in filter_dict.items()
    }

    project_employees: QuerySet[int] = project.employees_assigned.filter(
        employee__role=Employee.RoleChoices.EMPLOYEE
    ).values_list("employee_id", flat=True)

    for category in categories:
        user_answers: QuerySet[UserAnswer] = UserAnswer.objects.select_related(
            "question"
        ).filter(
            question__category_analytics=category,
            question__question_type=QuestionType.NUMBERS,
            question__poll__content_type=ContentType.objects.get_for_model(Project),
            question__poll__object_id=project.id,
            **user_answers_filters,
        )
        if curator_answers:
            user_answers = user_answers.filter(
                target_employee__id__in=project_employees
            )
        else:
            user_answers = user_answers.filter(
                employee__id__in=project_employees, target_employee=None
            )

        user_answers_aggregate: dict = user_answers.annotate(
            answer_as_float=Cast("answer", FloatField())
        ).aggregate(
            total_score=Sum("answer_as_float"),
            total_count=Count("id"),
        )

        # если нет ответов, то пропускаем категорию
        if not user_answers:
            project_stats.append(
                {
                    "category": category.value,
                    "category_display": category.label,
                    "value": None,
                }
            )
            continue

        total_score: int = user_answers_aggregate.get("total_score", 0)
        total_count: int = user_answers_aggregate.get("total_count", 0)

        if total_count == 0:
            project_stats.append(
                {
                    "category": category.value,
                    "category_display": category.label,
                    "value": None,
                }
            )
            continue

        average = round(total_score / total_count, 2)

        project_stats.append(
            {
                "category": category.value,
                "category_display": category.label,
                "value": average,
            }
        )

    return project_stats, None


def build_user_answers_filters(
    date_start: Optional[datetime], date_end: Optional[datetime]
) -> list[tuple[UserAnswer, dict[str, any]]]:
    """
    Создает фильтры для поиска ответов сотрудников.
    """
    user_answers_filters = []

    if date_start:
        user_answers_filters.append((UserAnswer, {"created_at__gte": date_start}))

    if date_end:
        next_day = date_end + timedelta(days=1)
        user_answers_filters.append((UserAnswer, {"created_at__date__lt": next_day}))

    return user_answers_filters


def check_validity_date_range(
    date_start: Optional[datetime], date_end: Optional[datetime]
) -> tuple[bool, Optional[str]]:
    """
    Проверяет чтобы дата начала была раньше даты окончания.
    """
    if date_start and date_end and date_start > date_end:
        return False, (
            f"Начальная дата не может быть позже конечной. {date_start} > {date_end}"
        )

    return True, None


def filter_projects(
    projects: QuerySet[Project],
    employees: QuerySet[Employee] = None,
    curators: QuerySet[Employee] = None,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    employee_status: str = None,
) -> tuple[Optional[QuerySet[Project]], Optional[str]]:
    if projects is None:
        return None, "Список проектов должен существовать."

    if date_start and date_end:
        correct, error = check_validity_date_range(date_start, date_end)
        if correct is False:
            return None, error

    if employees:
        projects, error = filter_projects_by_employees(projects, employees)
        if error:
            return None, error
        if not projects:
            return None, "Ни один проект не соответствует критериям фильтрации."

    if curators:
        projects, error = filter_projects_by_curators(projects, curators)
        if error:
            return None, error
        if not projects:
            return None, "Ни один проект не соответствует критериям фильтрации."

    if employee_status:
        projects, error = filter_projects_by_employee_status(projects, employee_status)
        if error:
            return None, error
        if not projects:
            return None, "Ни один проект не соответствует критериям фильтрации."

    return projects, None


def filter_projects_by_employees(
    projects: QuerySet[Project], employees: QuerySet[Employee]
) -> tuple[Optional[QuerySet[Project]], Optional[str]]:
    if not projects:
        return (
            None,
            "Ошибка при фильтрации проектов по сотрудникам. Список проектов должен существовать.",
        )
    if not employees:
        return projects, None
    return (
        projects.filter(
            employees_assigned__employee__id__in=[e.id for e in employees]
        ).distinct(),
        None,
    )


def filter_projects_by_curators(
    projects: QuerySet[Project], curators: QuerySet[Employee]
) -> tuple[Optional[QuerySet[Project]], Optional[str]]:
    if not projects:
        return (
            None,
            "Ошибка при фильтрации проектов по кураторам. Список проектов должен существовать.",
        )
    if not curators:
        return projects, None
    return (
        projects.filter(
            employees_assigned__employee__id__in=[c.id for c in curators]
        ).distinct(),
        None,
    )


def filter_projects_by_employee_status(
    projects: QuerySet[Project], employee_status: str
) -> tuple[Optional[QuerySet[Project]], Optional[str]]:
    if not projects:
        return (
            None,
            "Ошибка при фильтрации проектов по статусу сотрудника. Список проектов должен существовать.",
        )
    if not employee_status:
        return projects, None
    return (
        projects.filter(
            employees_assigned__employee__status=employee_status
        ).distinct(),
        None,
    )


def filter_employees(
    employees: QuerySet[Employee],
    projects: Optional[QuerySet[Project]] = None,
    curators: Optional[QuerySet[Employee]] = None,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    employee_status: str = None,
) -> tuple[Optional[QuerySet[Employee]], Optional[str]]:
    if not employees:
        return None, "Список сотрудников должен существовать."

    if date_start and date_end:
        correct, error = check_validity_date_range(date_start, date_end)
        if correct is False:
            return None, error

    if projects:
        employees, error = filter_employees_by_project(employees, projects)
        if error:
            return None, error
        if not employees:
            return None, "Ни один сотрудник не соответствует критериям фильтрации."

    if curators:
        employees, error = filter_employees_by_curators(employees, curators)
        if error:
            return None, error
        if not employees:
            return None, "Ни один сотрудник не соответствует критериям фильтрации."

    if employee_status:
        employees, error = filter_employees_by_employee_status(
            employees, employee_status
        )
        if error:
            return None, error
        if not employees:
            return None, "Ни один сотрудник не соответствует критериям фильтрации."

    return employees, None


def filter_employees_by_project(
    employees: QuerySet[Employee], projects: QuerySet[Project]
) -> tuple[Optional[QuerySet[Employee]], Optional[str]]:
    if not employees:
        return None, "Список сотрудников должен существовать."
    if not projects:
        return employees, None

    return (
        employees.filter(
            projects_assigned__project__id__in=[p.id for p in projects]
        ).distinct(),
        None,
    )


def filter_employees_by_curators(
    employees: QuerySet[Employee], curators: Optional[QuerySet[Employee]]
) -> tuple[Optional[QuerySet[Employee]], Optional[str]]:
    if not employees:
        return None, "Список сотрудников должен существовать."
    if not curators:
        return employees, None
    return (
        employees.filter(curators__curator__id__in=[c.id for c in curators]).distinct(),
        None,
    )


def filter_employees_by_employee_status(
    employees: QuerySet[Employee], employee_status: Optional[str]
) -> tuple[Optional[QuerySet[Employee]], Optional[str]]:
    if not employees:
        return None, "Список сотрудников должен существовать."
    if not employee_status:
        return employees, None
    return (
        employees.filter(status=employee_status).distinct(),
        None,
    )
