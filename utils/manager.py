"""Application operations shared by the CLI and tests."""

from models import Project, Task, User


class ProjectManager:
    """Manage users, projects, and tasks while keeping them persisted."""

    def __init__(self, store):
        """Load existing data from the provided store."""
        # Dependency injection lets the CLI and tests choose different files.
        self.store = store
        self.users = store.load()

    def _save(self):
        """Persist the current object graph after a change."""
        self.store.save(self.users)

    def add_user(self, name, email):
        """Create and save a user with a unique email address."""
        # Normalize emails so case differences do not create duplicate users.
        normalized_email = email.strip().lower()
        # any() stops checking as soon as one matching email is found.
        if any(user.email == normalized_email for user in self.users):
            raise ValueError(f"A user with email '{normalized_email}' already exists.")
        user = User(name, normalized_email)
        self.users.append(user)
        self._save()
        return user

    def find_user(self, user_id):
        """Return a user by ID or raise a helpful error."""
        # next(..., None) searches without raising StopIteration when absent.
        user = next((item for item in self.users if item.id == user_id), None)
        if user is None:
            raise ValueError(f"User #{user_id} was not found.")
        return user

    def add_project(self, user_id, title, description, due_date):
        """Create and save a project owned by a specific user."""
        user = self.find_user(user_id)
        project = Project(title, description, due_date)
        user.add_project(project)
        self._save()
        return project

    def all_projects(self, user_id=None):
        """Return owner/project pairs, optionally for one user."""
        # Wrapping one user in a list lets both branches use the same loop.
        users = [self.find_user(user_id)] if user_id is not None else self.users
        # This nested comprehension flattens each user's project list.
        return [(user, project) for user in users for project in user.projects]

    def find_project(self, project_id):
        """Return an owner/project pair by project ID."""
        match = next(
            (
                (user, project)
                for user in self.users
                for project in user.projects
                if project.id == project_id
            ),
            None,
        )
        if match is None:
            raise ValueError(f"Project #{project_id} was not found.")
        return match

    def edit_project(self, project_id, title=None, description=None, due_date=None):
        """Update supplied project fields and save the result."""
        # _ means the owner was returned but is not needed in this method.
        _, project = self.find_project(project_id)
        # None means the option was omitted, so only supplied fields change.
        if title is not None:
            project.title = title
        if description is not None:
            project.description = description
        if due_date is not None:
            project.due_date = due_date
        self._save()
        return project

    def add_task(self, project_id, title, assigned_to=None):
        """Create and save a task with zero or more contributors."""
        contributor_ids = list(assigned_to or [])
        # Validate every contributor before changing and saving the project.
        for user_id in contributor_ids:
            self.find_user(user_id)
        _, project = self.find_project(project_id)
        task = Task(title, contributor_ids)
        project.add_task(task)
        self._save()
        return task

    def all_tasks(self, project_id=None):
        """Return project/task pairs, optionally for one project."""
        if project_id is not None:
            _, project = self.find_project(project_id)
            return [(project, task) for task in project.tasks]
        # Flatten tasks from every project while retaining their parent project.
        return [
            (project, task)
            for _, project in self.all_projects()
            for task in project.tasks
        ]

    def find_task(self, task_id):
        """Return a project/task pair by task ID."""
        match = next(
            (
                (project, task)
                for project, task in self.all_tasks()
                if task.id == task_id
            ),
            None,
        )
        if match is None:
            raise ValueError(f"Task #{task_id} was not found.")
        return match

    def edit_task(self, task_id, title=None, status=None, assigned_to=None):
        """Update supplied task fields and save the result."""
        _, task = self.find_task(task_id)
        if title is not None:
            task.title = title
        if status is not None:
            task.status = status
        if assigned_to is not None:
            # An empty list intentionally clears all contributors; None means
            # the command did not request a contributor change.
            for user_id in assigned_to:
                self.find_user(user_id)
            task.assigned_to = list(assigned_to)
        self._save()
        return task

    def complete_task(self, task_id):
        """Mark a task complete and save the result."""
        _, task = self.find_task(task_id)
        task.complete()
        self._save()
        return task