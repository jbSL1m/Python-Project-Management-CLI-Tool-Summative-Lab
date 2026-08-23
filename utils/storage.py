"""JSON persistence helpers for project management data."""

import json
from pathlib import Path

from models import User


class JsonStore:
    """Load and save the application's object graph in one JSON file."""

    def __init__(self, path):
        """Remember where application data should be stored."""
        self.path = Path(path)

    def load(self):
        """Load users from JSON, returning an empty list for a missing file."""
        try:
            with self.path.open(encoding="utf-8") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            # A missing file is normal on the application's first run.
            return []
        except (json.JSONDecodeError, OSError) as error:
            # Convert low-level file/JSON errors into one message for the CLI.
            raise ValueError(f"Could not read data file '{self.path}': {error}") from error

        # Check the outer JSON shape before trying to create model objects.
        if not isinstance(data, dict) or not isinstance(data.get("users"), list):
            raise ValueError("Data file must contain a 'users' list.")

        try:
            # from_dict recursively rebuilds each user's projects and tasks.
            return [User.from_dict(user) for user in data["users"]]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Data file contains invalid records: {error}") from error

    def save(self, users):
        """Write all users and their nested data to JSON."""
        # parents=True creates every missing directory in the path.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = {"users": [user.to_dict() for user in users]}

        try:
            # Write a complete temporary file before replacing the real file.
            # This reduces the chance of leaving half-written JSON behind.
            with temporary_path.open("w", encoding="utf-8") as data_file:
                json.dump(payload, data_file, indent=2)
                data_file.write("\n")
            temporary_path.replace(self.path)
        except OSError as error:
            raise ValueError(f"Could not save data file '{self.path}': {error}") from error