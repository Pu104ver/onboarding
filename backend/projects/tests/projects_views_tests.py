import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from projects.models import Project
from employees.models import Employee


@pytest.mark.django_db
def test_create_project():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="admin", password="adminpass")
    Employee.objects.create(
        user=user, telegram_nickname="admin", role=Employee.RoleChoices.ADMIN
    )
    client.force_authenticate(user=user)
    url = reverse("project-list")
    data = {
        "name": "Test Project",
    }

    # Act
    response = client.post(url, data, format="json")

    # Assert
    assert response.status_code == 201
    assert response.data["name"] == "Test Project"


@pytest.mark.django_db
def test_list_projects():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="admin", password="adminpass")
    Project.objects.create(name="Test Project")
    client.force_authenticate(user=user)
    url = reverse("project-list")

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.data[0]["name"] == "Test Project"
