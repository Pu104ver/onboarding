import pytest
from django.contrib.auth import get_user_model
from employees.models import Employee
from comments.models import Comment


@pytest.mark.django_db
def test_comment_creation():
    # Arrange
    User = get_user_model()
    user_employee = User.objects.create_user(
        username="testuser_employee", password="testpass"
    )
    employee = Employee.objects.create(
        user=user_employee,
        telegram_nickname="testuser_employee",
        role=Employee.RoleChoices.EMPLOYEE,
    )
    user_author = User.objects.create_user(
        username="testuser_author", password="testpass"
    )
    author = Employee.objects.create(
        user=user_author,
        telegram_nickname="testuser_author",
        role=Employee.RoleChoices.EMPLOYEE,
    )

    # Act
    comment = Comment.objects.create(
        employee=employee, author=author, text="Test comment"
    )

    # Assert
    assert comment.employee == employee
    assert comment.author == author
    assert comment.text == "Test comment"
    assert comment.created_at is not None
