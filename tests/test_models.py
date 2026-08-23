"""Unit tests for the object model."""

import pytest

from models import Project, Task, User


def test_user_project_task_relationships():
    """Users should own projects and projects should own tasks."""
    user = User("Ada Lovelace", "ada@example.com")
    project = Project("Compiler", "Build an engine", "2026-10-01")
    task = Task("Write parser", [user.id])

    project.add_task(task)
    user.add_project(project)

    assert user.find_project(project.id) is project
    assert project.find_task(task.id) is task
    assert task.assigned_to == [user.id]


def test_task_complete_changes_status():
    """Completing a task should update its validated status property."""
    task = Task("Ship release")

    task.complete()

    assert task.status == "complete"


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: User("", "valid@example.com"), "Name cannot be empty"),
        (lambda: User("Valid", "invalid"), "valid email"),
        (lambda: Project("Title", "Description", "tomorrow"), "YYYY-MM-DD"),
        (lambda: Task("Title", status="started"), "pending.*complete"),
    ],
)
def test_model_properties_reject_invalid_values(factory, message):
    """Property setters should reject malformed model data."""
    with pytest.raises(ValueError, match=message):
        factory()


def test_nested_models_round_trip_to_dictionary():
    """Nested models should survive conversion to and from stored data."""
    user = User("Grace Hopper", "grace@example.com")
    project = Project("COBOL", "Language project", "2026-11-15")
    project.add_task(Task("Write specification", [user.id]))
    user.add_project(project)

    restored = User.from_dict(user.to_dict())

    assert restored.to_dict() == user.to_dict()