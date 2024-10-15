import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
def test_get_users_list():
    # Arrange
    client = APIClient()
    User = get_user_model()
    user1 = User.objects.create_user(username="testuser1", password="testpass")
    user2 = User.objects.create_user(username="testuser2", password="testpass")
    client.force_authenticate(user=user1)
    url = reverse("user-list")

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]["username"] == "testuser1"
    assert response.data[1]["username"] == "testuser2"


@pytest.mark.django_db
def test_create_user_via_api():
    # Arrange
    client = APIClient()
    User = get_user_model()
    admin_user = User.objects.create_user(
        username="admin", password="adminpass", is_staff=True
    )
    client.force_authenticate(user=admin_user)
    url = reverse("user-list")
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass",
    }

    # Act
    response = client.post(url, data, format="json")

    # Assert
    assert response.status_code == 201
    assert User.objects.count() == 2
    new_user = User.objects.get(username="newuser")
    assert new_user.email == "newuser@example.com"
    assert new_user.is_staff == False
    assert new_user.is_active == True
