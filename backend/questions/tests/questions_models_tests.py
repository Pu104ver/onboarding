import pytest
from django.contrib.auth import get_user_model
from employees.models import Employee
from questions.models import (
    PollQuestion,
    Question,
    QuestionType,
    UserAnswer,
    ContentType,
)
from projects.models import Project
from datetime import date


@pytest.mark.django_db
def test_question_creation():
    # Arrange
    project_content_type = ContentType.objects.get_for_model(Project)
    poll = PollQuestion.objects.create(
        title="Тест тайтл",
        message="Тест меседж",
        content_type=project_content_type,
        object_id=1,
    )

    # Act
    question = Question.objects.create(
        poll=poll, text="Тест вопрос", question_type=QuestionType.YES_NO
    )

    # Assert
    assert question.poll.title == "Тест тайтл"
    assert question.text == "Тест вопрос"
    assert question.question_type == QuestionType.YES_NO


@pytest.mark.django_db
def test_answer_creation():
    # Arrange
    project_content_type = ContentType.objects.get_for_model(Project)
    poll = PollQuestion.objects.create(
        title="Тест тайтл",
        message="Тест меседж",
        content_type=project_content_type,
        object_id=1,
    )
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="testpass")
    employee = Employee.objects.create(
        user=user,
        full_name="Test Employee",
        telegram_nickname="testemployee",
        date_of_employment=date(2024, 1, 1),
    )
    question = Question.objects.create(
        poll=poll, text="Тест вопрос", question_type=QuestionType.YES_NO
    )

    # Act
    user_answer = UserAnswer.objects.create(
        employee=employee, question=question, answer="Тест ответ"
    )

    # Assert
    assert user_answer.employee == employee
    assert user_answer.question == question
    assert user_answer.answer == "Тест ответ"
