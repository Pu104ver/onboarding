import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from employees.models import Employee, CuratorEmployees
from datetime import date

User = get_user_model()


@pytest.mark.django_db
def test_get_employees_list():
    # Arrange
    client = APIClient()
    user = User.objects.create_user(username="admin", password="adminpass")
    client.force_authenticate(user=user)

    user_curator = User.objects.create_user(username="curator", password="curatorpass")
    curator = Employee.objects.create(
        user=user_curator,
        full_name="Test Curator",
        role=Employee.RoleChoices.CURATOR,
        telegram_nickname="testcurator",
    )

    user_employee = User.objects.create_user(
        username="employeeuser", password="employeepass"
    )
    employee = Employee.objects.create(
        user=user_employee,
        full_name="Test Employee",
        telegram_nickname="testemployee",
        date_of_employment=date(2024, 1, 1),
        role=Employee.RoleChoices.EMPLOYEE,
    )
    CuratorEmployees.objects.create(curator=curator, employee=employee)

    url = reverse("employee-list")

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["full_name"] == "Test Curator"
    assert response.data[0]["telegram_nickname"] == "testcurator"
    assert response.data[0]["role"] == Employee.RoleChoices.CURATOR
    assert response.data[1]["full_name"] == "Test Employee"
    assert response.data[1]["telegram_nickname"] == "testemployee"
    assert response.data[1]["date_of_employment"] == "2024-01-01"


@pytest.mark.django_db
def test_create_employee():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(
        username="admin", password="adminpass", is_staff=True
    )
    employee = Employee.objects.create(
        user=user,
        full_name="Admin Employee",
        telegram_nickname="testemployee",
        role=Employee.RoleChoices.ADMIN,
    )
    client.force_authenticate(user=user)

    url = reverse("employee-list")
    data = {
        "full_name": "Test Employee",
        "telegram_nickname": "testemployee",
        "date_of_employment": "2024-01-01",
        "role": f"{Employee.RoleChoices.EMPLOYEE}",
    }

    # Act
    response = client.post(url, data, format="json")

    # Assert
    assert response.status_code == 201
    assert "employee_id" in response.data
    assert "uid" in response.data
    assert "token" in response.data
    assert Employee.objects.count() == 2

    # Act
    employee = Employee.objects.get(full_name="Test Employee")

    # Assert
    assert employee.full_name == "Test Employee"
    assert employee.telegram_nickname == "testemployee"
    assert employee.date_of_employment == date(2024, 1, 1)


@pytest.mark.django_db
def test_update_employee():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(
        username="admin", password="adminpass", is_staff=True
    )

    employee = Employee.objects.create(
        user=user,
        full_name="Test Employee",
        telegram_nickname="testemployee",
        date_of_employment=date(2024, 1, 1),
        role=Employee.RoleChoices.ADMIN,
    )

    client.force_authenticate(user=user)
    url = reverse("employee-detail", args=[employee.id])
    data = {
        "full_name": "Updated Employee",
        "telegram_nickname": "updatedemployee",
        "date_of_employment": "2024-02-01",
        "role": f"{Employee.RoleChoices.EMPLOYEE}",
    }

    # Act
    response = client.patch(url, data, format="json")

    # Assert
    assert response.status_code == 200
    assert response.data["full_name"] == "Updated Employee"
    assert response.data["telegram_nickname"] == "updatedemployee"
    assert response.data["date_of_employment"] == "2024-02-01"
