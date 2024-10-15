import pytest
from django.contrib.auth import get_user_model
from employees.models import Employee, CuratorEmployees
from projects.models import Project
from datetime import date

User = get_user_model()


@pytest.mark.django_db
def test_create_employee():
    # Arrange
    user_curator = User.objects.create_user(
        username="curatoruser", password="curatorpass"
    )
    curator = Employee.objects.create(
        user=user_curator,
        full_name="Test Curator",
        role=Employee.RoleChoices.CURATOR,
        telegram_nickname="testcurator",
    )

    user_employee = User.objects.create_user(
        username="employeeuser", password="employeepass"
    )
    project = Project.objects.create(name="Test Project")

    # Act
    employee = Employee.objects.create(
        user=user_employee,
        full_name="Test Employee",
        telegram_nickname="testemployee",
        date_of_employment=date(2024, 1, 1),
    )
    employee.projects.add(project)
    CuratorEmployees.objects.create(curator=curator, employee=employee)

    # Assert
    assert Employee.objects.count() == 2  # 1 curator + 1 employee
    assert employee.user == user_employee
    assert employee.full_name == "Test Employee"
    assert employee.telegram_nickname == "testemployee"
    assert employee.date_of_employment == date(2024, 1, 1)
    assert list(employee.projects.all()) == [project]
    assert CuratorEmployees.objects.filter(employee=employee, curator=curator).exists()


@pytest.mark.django_db
def test_archive_employee():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user, telegram_nickname="testemployee", role=Employee.RoleChoices.EMPLOYEE
    )

    # Assert initial state
    assert employee.is_archived == False

    # Act
    employee.is_archived = True
    employee.save()

    # Assert
    assert employee.is_archived == True


@pytest.mark.django_db
def test_soft_delete_employee():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")

    # Act
    employee = Employee.objects.create(
        user=user, telegram_nickname="testemployee", role=Employee.RoleChoices.EMPLOYEE
    )

    # Assert
    assert Employee.objects.count() == 1
    assert Employee.all_objects.count() == 1

    # Act
    employee.delete()

    # Assert
    assert Employee.objects.count() == 0
    assert Employee.all_objects.count() == 1
    assert employee.is_deleted == True
    assert employee.deleted_at is not None


@pytest.mark.django_db
def test_hard_delete_employee():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")

    # Act
    employee = Employee.objects.create(
        user=user, telegram_nickname="testemployee", role=Employee.RoleChoices.EMPLOYEE
    )

    # Assert
    assert Employee.objects.count() == 1
    assert Employee.all_objects.count() == 1

    # Act
    employee.hard_delete()

    # Assert
    assert Employee.objects.count() == 0
    assert Employee.all_objects.count() == 0
