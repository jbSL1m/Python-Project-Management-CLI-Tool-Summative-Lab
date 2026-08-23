"""Tests for command parsing, output, and persisted CLI behavior."""

import json

import pytest

from main import main


def run_cli(data_file, *arguments):
    """Run a command against an isolated test data file."""
    return main(["--data-file", str(data_file), *arguments])


def test_complete_cli_workflow(tmp_path, capsys):
    """Commands should create related records and persist task completion."""
    data_file = tmp_path / "project_data.json"

    assert run_cli(data_file, "add-user", "Ada", "ada@example.com") == 0
    data = json.loads(data_file.read_text(encoding="utf-8"))
    user_id = data["users"][0]["id"]

    assert run_cli(
        data_file,
        "add-project",
        str(user_id),
        "CLI Tool",
        "Manage work",
        "2026-12-01",
    ) == 0
    data = json.loads(data_file.read_text(encoding="utf-8"))
    project_id = data["users"][0]["projects"][0]["id"]

    assert run_cli(
        data_file,
        "add-task",
        str(project_id),
        "Write tests",
        "--assigned-to",
        str(user_id),
    ) == 0
    data = json.loads(data_file.read_text(encoding="utf-8"))
    task_id = data["users"][0]["projects"][0]["tasks"][0]["id"]

    assert run_cli(data_file, "complete-task", str(task_id)) == 0
    assert run_cli(data_file, "list-tasks") == 0

    output = capsys.readouterr().out
    assert "Write tests" in output
    assert "complete" in output
    assert "Ada" in output


def test_edit_commands_persist_changes(tmp_path):
    """Project and task edit commands should update JSON data."""
    data_file = tmp_path / "project_data.json"
    run_cli(data_file, "add-user", "Dev", "dev@example.com")
    data = json.loads(data_file.read_text(encoding="utf-8"))
    user_id = data["users"][0]["id"]
    run_cli(data_file, "add-project", str(user_id), "Old", "Old", "2026-10-01")
    data = json.loads(data_file.read_text(encoding="utf-8"))
    project_id = data["users"][0]["projects"][0]["id"]
    run_cli(data_file, "add-task", str(project_id), "Old task")
    data = json.loads(data_file.read_text(encoding="utf-8"))
    task_id = data["users"][0]["projects"][0]["tasks"][0]["id"]

    run_cli(data_file, "edit-project", str(project_id), "--title", "New project")
    run_cli(data_file, "edit-task", str(task_id), "--title", "New task")

    data = json.loads(data_file.read_text(encoding="utf-8"))
    project = data["users"][0]["projects"][0]
    assert project["title"] == "New project"
    assert project["tasks"][0]["title"] == "New task"


def test_cli_reports_unknown_contributor(tmp_path, capsys):
    """Contributor IDs must refer to existing users."""
    data_file = tmp_path / "project_data.json"
    run_cli(data_file, "add-user", "Dev", "dev@example.com")
    data = json.loads(data_file.read_text(encoding="utf-8"))
    user_id = data["users"][0]["id"]
    run_cli(data_file, "add-project", str(user_id), "Project", "Description", "2026-10-01")
    data = json.loads(data_file.read_text(encoding="utf-8"))
    project_id = data["users"][0]["projects"][0]["id"]

    with pytest.raises(SystemExit) as error:
        run_cli(data_file, "add-task", str(project_id), "Task", "--assigned-to", "999")

    assert error.value.code == 2
    assert "User #999 was not found" in capsys.readouterr().err