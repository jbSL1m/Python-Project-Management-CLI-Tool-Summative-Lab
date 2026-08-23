"""Command-line entry point for the project management tool."""

import argparse
from pathlib import Path
import sys

from tabulate import tabulate

from utils import JsonStore, ProjectManager


DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "project_data.json"


def print_table(headers, rows, empty_message):
    """Print rows as a table or show a useful empty-state message."""
    if rows:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        print(empty_message)


def build_parser():
    """Create and return the complete argparse command structure."""
    # The main parser handles options shared by every command.
    parser = argparse.ArgumentParser(description="Manage team projects and tasks.")
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help="JSON storage path (default: data/project_data.json)",
    )
    # Subparsers give each command its own positional and optional arguments.
    # dest="command" stores the selected command name on the parsed args object.
    commands = parser.add_subparsers(dest="command", required=True)

    add_user = commands.add_parser("add-user", help="Create a user")
    add_user.add_argument("name")
    add_user.add_argument("email")

    commands.add_parser("list-users", help="List all users")

    add_project = commands.add_parser("add-project", help="Add a project to a user")
    add_project.add_argument("user_id", type=int)
    add_project.add_argument("title")
    add_project.add_argument("description")
    add_project.add_argument("due_date", help="Date in YYYY-MM-DD format")

    list_projects = commands.add_parser("list-projects", help="List projects")
    list_projects.add_argument("--user-id", type=int)

    edit_project = commands.add_parser("edit-project", help="Edit a project")
    edit_project.add_argument("project_id", type=int)
    edit_project.add_argument("--title")
    edit_project.add_argument("--description")
    edit_project.add_argument("--due-date")

    add_task = commands.add_parser("add-task", help="Add a task to a project")
    add_task.add_argument("project_id", type=int)
    add_task.add_argument("title")
    # nargs="*" accepts zero or more contributor IDs after this option.
    add_task.add_argument("--assigned-to", nargs="*", type=int, default=[])

    list_tasks = commands.add_parser("list-tasks", help="List tasks")
    list_tasks.add_argument("--project-id", type=int)

    edit_task = commands.add_parser("edit-task", help="Edit a task")
    edit_task.add_argument("task_id", type=int)
    edit_task.add_argument("--title")
    edit_task.add_argument("--status", choices=sorted({"pending", "complete"}))
    edit_task.add_argument("--assigned-to", nargs="*", type=int)

    complete_task = commands.add_parser("complete-task", help="Complete a task")
    complete_task.add_argument("task_id", type=int)
    return parser


def run_command(args, manager):
    """Run the selected command and print its result."""
    # argparse has already validated argument types before this dispatch begins.
    if args.command == "add-user":
        user = manager.add_user(args.name, args.email)
        print(f"Created user {user}.")
    elif args.command == "list-users":
        rows = [(user.id, user.name, user.email) for user in manager.users]
        print_table(["ID", "Name", "Email"], rows, "No users found.")
    elif args.command == "add-project":
        project = manager.add_project(
            args.user_id, args.title, args.description, args.due_date
        )
        print(f"Created project {project}.")
    elif args.command == "list-projects":
        rows = [
            (project.id, project.title, owner.name, project.due_date)
            for owner, project in manager.all_projects(args.user_id)
        ]
        print_table(["ID", "Project", "Owner", "Due date"], rows, "No projects found.")
    elif args.command == "edit-project":
        project = manager.edit_project(
            args.project_id, args.title, args.description, args.due_date
        )
        print(f"Updated project {project}.")
    elif args.command == "add-task":
        task = manager.add_task(args.project_id, args.title, args.assigned_to)
        print(f"Created task {task}.")
    elif args.command == "list-tasks":
        # This dictionary translates stored contributor IDs into display names.
        users_by_id = {user.id: user.name for user in manager.users}
        rows = [
            (
                task.id,
                task.title,
                project.title,
                task.status,
                ", ".join(users_by_id.get(user_id, f"#{user_id}") for user_id in task.assigned_to)
                or "Unassigned",
            )
            for project, task in manager.all_tasks(args.project_id)
        ]
        print_table(
            ["ID", "Task", "Project", "Status", "Contributors"],
            rows,
            "No tasks found.",
        )
    elif args.command == "edit-task":
        task = manager.edit_task(args.task_id, args.title, args.status, args.assigned_to)
        print(f"Updated task {task}.")
    elif args.command == "complete-task":
        task = manager.complete_task(args.task_id)
        print(f"Completed task {task}.")


def main(argv=None):
    """Parse command-line arguments and return an operating-system exit code."""
    parser = build_parser()
    # argv is useful in tests; None tells argparse to read the real terminal.
    args = parser.parse_args(argv)
    try:
        manager = ProjectManager(JsonStore(args.data_file))
        run_command(args, manager)
    except ValueError as error:
        # parser.error prints a friendly message and exits with status code 2.
        parser.error(str(error))
    return 0


# This guard prevents the CLI from running when main.py is imported by tests.
if __name__ == "__main__":
    sys.exit(main())