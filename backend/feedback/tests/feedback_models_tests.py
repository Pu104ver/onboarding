import pytest
from django.contrib.auth import get_user_model
from employees.models import Employee
from feedback.models import FeedbackUser

User = get_user_model()


@pytest.mark.django_db
def test_create_feedback():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user, full_name="Test Employee", role=Employee.RoleChoices.EMPLOYEE, telegram_nickname="test"
    )

    # Act
    feedback = FeedbackUser.objects.create(
        employee=employee,
        text="Test feedback message",
    )

    # Assert
    assert FeedbackUser.objects.count() == 1
    assert feedback.employee == employee
    assert feedback.text == "Test feedback message"
    assert feedback.created_at is not None


@pytest.mark.django_db
def test_feedback_str_representation():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user, full_name="Test Employee", role=Employee.RoleChoices.EMPLOYEE, telegram_nickname="test"
    )
    feedback = FeedbackUser.objects.create(
        employee=employee,
        text="Test feedback message",
    )

    # Assert
    assert str(feedback) == "Test Employee - Test feedback messag..."


@pytest.mark.django_db
def test_soft_delete_feedback():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user, full_name="Test Employee", role=Employee.RoleChoices.EMPLOYEE, telegram_nickname="test"
    )
    feedback = FeedbackUser.objects.create(
        employee=employee,
        text="Test feedback message",
    )

    # Assert initial state
    assert FeedbackUser.objects.count() == 1
    assert FeedbackUser.all_objects.count() == 1

    # Act
    feedback.delete()

    # Assert
    assert FeedbackUser.objects.count() == 0
    assert FeedbackUser.all_objects.count() == 1
    assert feedback.is_deleted == True
    assert feedback.deleted_at is not None


@pytest.mark.django_db
def test_hard_delete_feedback():
    # Arrange
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user, full_name="Test Employee", role=Employee.RoleChoices.EMPLOYEE, telegram_nickname="test"
    )
    feedback = FeedbackUser.objects.create(
        employee=employee,
        text="Test feedback message",
    )

    # Assert initial state
    assert FeedbackUser.objects.count() == 1
    assert FeedbackUser.all_objects.count() == 1

    # Act
    feedback.hard_delete()

    # Assert
    assert FeedbackUser.objects.count() == 0
    assert FeedbackUser.all_objects.count() == 0
