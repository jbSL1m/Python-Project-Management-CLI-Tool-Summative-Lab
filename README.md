# Python-Project-Management-CLI-Tool-Summative-Lab

The Scenario: Create a Command-Line Project Management Tool 
You are tasked with creating a command-line project management tool for a team of developers. The tool should allow administrators to manage users, projects, and tasks through structured CLI commands. The system must support:

Create and list users via the command line.
Add projects to specific users and display their associated projects.
Assign tasks to projects and mark them as complete.
Edit and persist project/task data using file I/O.
Navigate the tool with clear, user-friendly CLI commands.
Manage data relationships like one-to-many (users to projects) and many-to-many (projects to tasks with contributors).
Create and manage users, projects, and tasks.

Design a CLI tool that enables:

Admins to manage users and projects.
Each user to have one or more projects.
Each project to have one or more tasks.
CLI commands to add, view, and update these entities.

Classes: User, Project, Task
Relationships:
One-to-many: User -> Projects
One-to-many: Project -> Tasks
Attributes
Users: name, email
Projects: title, description, due_date
Tasks: title, status, assigned_to
File Structure
main.py: CLI entry point
models/: contains class definitions
data/: local JSON or CSV file storage
utils/: helper functions, custom hooks
Persistence
Use JSON for saving/loading users, projects, and tasks
Package Setup:
External dependencies listed in requirements.txt

Set Up CLI Entry
Use argparse to define CLI structure.
Implement subcommands like add-user, list-projects, and complete-task.
Build Object Model
Use classes for User, Project, and Task.
Apply __init__, instance methods, and relationships.
Use class methods to create or retrieve object collections.
Implement __str__() or __repr__() for clean CLI output.
Add OOP Features
Use @property and setter methods to control access to attributes.
Use class attributes (e.g., ID counters).
Add inheritance where appropriate (e.g., Person → User).
Configure File IO
Save and load objects via JSON files.
Handle missing files or malformed data with try-except.
Use Python scripting best practices (if __name__ == "__main__").
Use External Packages
Install and use at least one PyPi package (e.g., rich, tabulate, typer).
Track packages in requirements.txt.

Add unit tests for your class methods and CLI logic.
Test input/output interactions using mock data.
Use print/logging/debugger to trace logic.
Refactor large files into reusable modules.

Comment on all class methods and utility functions.
Create a README.md with:
Setup instructions
How to run CLI commands
Overview of features and known issues
Ensure all code is pushed to GitHub.
