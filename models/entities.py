"""Object models for users, projects, and tasks."""

from datetime import date


class Person:
    """Base class for people stored by the application."""

    def __init__(self, name, email):
        """Create a person with a validated name and email address."""
        # These assignments use the property setters below, so new objects are
        # validated in the same way as later updates.
        self.name = name
        self.email = email

    @property
    def name(self):
        """Return the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Require a non-empty name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name cannot be empty.")
        # _name is the backing attribute used internally by the name property.
        self._name = value.strip()

    @property
    def email(self):
        """Return the person's email address."""
        return self._email

    @email.setter
    def email(self, value):
        """Require a basic email-shaped value."""
        if not isinstance(value, str) or "@" not in value or value.startswith("@"):
            raise ValueError("Enter a valid email address.")
        self._email = value.strip().lower()


class Task:
    """A unit of work belonging to a project."""

    # Class attributes are shared by every Task object.
    _next_id = 1
    VALID_STATUSES = {"pending", "complete"}

    def __init__(self, title, assigned_to=None, status="pending", task_id=None):
        """Create a task and assign a stable numeric ID."""
        # New tasks use the counter. Loaded tasks reuse their saved ID.
        self.id = task_id if task_id is not None else Task._next_id
        # max() moves the counter past loaded IDs and prevents duplicate IDs.
        Task._next_id = max(Task._next_id, self.id + 1)
        self.title = title
        self.status = status
        # Create a new list so Task objects never accidentally share one list.
        self.assigned_to = list(assigned_to or [])

    @property
    def title(self):
        """Return the task title."""
        return self._title

    @title.setter
    def title(self, value):
        """Require a non-empty task title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task title cannot be empty.")
        self._title = value.strip()

    @property
    def status(self):
        """Return the task status."""
        return self._status

    @status.setter
    def status(self, value):
        """Allow only supported task statuses."""
        if value not in self.VALID_STATUSES:
            raise ValueError("Status must be 'pending' or 'complete'.")
        self._status = value

    def complete(self):
        """Mark the task as complete."""
        self.status = "complete"

    def to_dict(self):
        """Convert the task to JSON-compatible data."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a task from stored JSON data."""
        # cls refers to the class itself, making this an alternate constructor.
        return cls(
            data["title"],
            data.get("assigned_to", []),
            data.get("status", "pending"),
            data["id"],
        )

    def __str__(self):
        """Return a readable task summary for CLI output."""
        return f"#{self.id} {self.title} [{self.status}]"


class Project:
    """A project owned by one user and containing tasks."""

    _next_id = 1

    def __init__(self, title, description, due_date, tasks=None, project_id=None):
        """Create a project with an optional collection of tasks."""
        self.id = project_id if project_id is not None else Project._next_id
        Project._next_id = max(Project._next_id, self.id + 1)
        self.title = title
        self.description = description
        self.due_date = due_date
        self.tasks = list(tasks or [])

    @property
    def title(self):
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value):
        """Require a non-empty project title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Project title cannot be empty.")
        self._title = value.strip()

    @property
    def due_date(self):
        """Return the due date as an ISO date string."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        """Require a date in YYYY-MM-DD format."""
        try:
            # fromisoformat validates the string without an external package.
            date.fromisoformat(value)
        except (TypeError, ValueError) as error:
            # "from error" keeps the original exception as debugging context.
            raise ValueError("Due date must use YYYY-MM-DD format.") from error
        self._due_date = value

    def add_task(self, task):
        """Add a task to this project."""
        self.tasks.append(task)

    def find_task(self, task_id):
        """Return a task by ID, or None when it is not present."""
        # next() returns the first match; its second argument is the fallback.
        return next((task for task in self.tasks if task.id == task_id), None)

    def to_dict(self):
        """Convert the project and its tasks to JSON-compatible data."""
        # JSON cannot save custom objects directly, so nested tasks become dicts.
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        """Build a project and its tasks from stored JSON data."""
        # Rebuild child Task objects before creating their parent Project.
        tasks = [Task.from_dict(task) for task in data.get("tasks", [])]
        return cls(
            data["title"],
            data.get("description", ""),
            data["due_date"],
            tasks,
            data["id"],
        )

    def __str__(self):
        """Return a readable project summary for CLI output."""
        return f"#{self.id} {self.title} (due {self.due_date})"


class User(Person):
    """A team member who owns projects."""

    _next_id = 1

    def __init__(self, name, email, projects=None, user_id=None):
        """Create a user with an optional collection of projects."""
        # super() runs Person.__init__ so User reuses its validation logic.
        super().__init__(name, email)
        self.id = user_id if user_id is not None else User._next_id
        User._next_id = max(User._next_id, self.id + 1)
        self.projects = list(projects or [])

    def add_project(self, project):
        """Add a project owned by this user."""
        self.projects.append(project)

    def find_project(self, project_id):
        """Return a project by ID, or None when it is not present."""
        return next((project for project in self.projects if project.id == project_id), None)

    def to_dict(self):
        """Convert the user and owned projects to JSON-compatible data."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "projects": [project.to_dict() for project in self.projects],
        }

    @classmethod
    def from_dict(cls, data):
        """Build a user and owned projects from stored JSON data."""
        # Loading proceeds from the deepest children upward: tasks, projects,
        # and finally the user that owns the complete object graph.
        projects = [Project.from_dict(project) for project in data.get("projects", [])]
        return cls(data["name"], data["email"], projects, data["id"])

    def __str__(self):
        """Return a readable user summary for CLI output."""
        return f"#{self.id} {self.name} <{self.email}>"