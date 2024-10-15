import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from employees.models import Employee


@pytest.mark.django_db
def test_create_comment():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="admin", password="adminpass")
    employee = Employee.objects.create(
        user=user, telegram_nickname="admin", role=Employee.RoleChoices.ADMIN
    )
    client.force_authenticate(user=user)
    url = reverse("comment-list")

    user_author = User.objects.create_user(
        username="testuser_author", password="testpass"
    )
    author = Employee.objects.create(
        user=user_author,
        telegram_nickname="testuser_author",
        role=Employee.RoleChoices.EMPLOYEE,
    )

    data = {"employee": employee.id, "author": author.id, "text": "Test comment"}

    # Act
    response = client.post(url, data, format="json")

    # Assert
    assert response.status_code == 201
    assert response.data["employee"] == employee.id
    assert response.data["author"] == author.id
    assert response.data["text"] == "Test comment"
