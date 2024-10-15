import pytest
from projects.models import Project


@pytest.mark.django_db
def test_project_creation():
    # Act
    project = Project.objects.create(name="Test Project")

    # Assert
    assert project.name == "Test Project"
