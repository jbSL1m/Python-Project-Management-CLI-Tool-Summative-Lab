# Project Management CLI

A command-line tool for managing team users, projects, tasks, and contributors.
Data is saved to a local JSON file after every change.

## Features

- Create and list users.
- Add projects to users and filter projects by owner.
- Add tasks to projects and assign multiple contributors.
- Edit project and task details.
- Mark tasks complete.
- Validate emails, due dates, statuses, IDs, and duplicate users.
- Display lists as readable tables using `tabulate`.
- Recover cleanly from missing files and report malformed JSON.

## Setup

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Commands

Run commands from the repository root. Values containing spaces must be quoted.

```bash
# Users
python main.py add-user "Ada Lovelace" ada@example.com
python main.py list-users

# Projects
python main.py add-project 1 "CLI Tool" "Manage team work" 2026-12-01
python main.py list-projects
python main.py list-projects --user-id 1
python main.py edit-project 1 --title "Project Manager" --due-date 2027-01-15

# Tasks and contributors
python main.py add-task 1 "Write tests" --assigned-to 1 2
python main.py list-tasks
python main.py list-tasks --project-id 1
python main.py edit-task 1 --title "Write integration tests" --assigned-to 2
python main.py complete-task 1
```

Use `python main.py --help` or `python main.py COMMAND --help` for built-in help.
The optional `--data-file PATH` argument selects another JSON file and must come
before the command:

```bash
python main.py --data-file data/demo.json list-users
```

## Data Model

- `User` inherits shared name and email behavior from `Person`.
- One user owns many projects.
- One project contains many tasks.
- A task stores multiple contributor user IDs, allowing users to contribute to
	many tasks and tasks to have many contributors.
- Class-level counters assign stable numeric IDs. Loading JSON advances the
	counters so new records do not reuse persisted IDs.

The default data file is `data/project_data.json`. Writes first go to a temporary
file and are then moved into place to reduce the chance of partial JSON data.

## Tests

```bash
python -m pytest
```

Tests cover model validation, relationships, JSON round trips, malformed files,
CLI output, editing, contributor validation, and task completion.

## Known Issues

- This local tool has no authentication or permission roles.
- Concurrent processes can overwrite each other's changes because there is no
	file locking.
- Deleting users, projects, and tasks is not currently supported.
