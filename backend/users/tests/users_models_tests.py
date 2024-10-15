import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    # Arrange
    username = "testuser"
    email = "testuser@example.com"
    password = "password123"
    first_name = "John"
    last_name = "Doe"

    # Act
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    # Assert
    assert user.username == username
    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.is_active


@pytest.mark.django_db
def test_update_user():
    # Arrange
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser", email="testuser@example.com", password="testpass"
    )

    # Act
    user.first_name = "Test"
    user.last_name = "User"
    user.save()

    # Assert
    updated_user = User.objects.get(id=user.id)
    assert updated_user.first_name == "Test"
    assert updated_user.last_name == "User"


@pytest.mark.django_db
def test_create_superuser():
    # Arrange
    username = "admin"
    email = "admin@example.com"
    password = "adminpassword"

    # Act
    admin_user = User.objects.create_superuser(
        username=username, email=email, password=password
    )

    # Assert
    assert admin_user.username == username
    assert admin_user.email == email
    assert admin_user.is_staff
    assert admin_user.is_superuser
    assert admin_user.is_active
