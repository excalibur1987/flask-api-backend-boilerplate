# -*- coding: utf-8 -*-
"""Click commands."""
import os
import re
from getpass import getpass
from subprocess import call
from typing import TYPE_CHECKING, List

import click
from flask import Flask, current_app
from flask.cli import with_appcontext
from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import MethodNotAllowed, NotFound

if TYPE_CHECKING:
    from app.apis.v1.users.models import User


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, "--verbose"])
    exit(rv)


def getfiles_paths(path: str) -> List[str]:

    files: List[str] = []

    for dirpath, dirs, filenames in os.walk(path):

        files = files + [os.path.abspath(os.path.join(dirpath, f)) for f in filenames]

        for dir in dirs:
            files = files + getfiles_paths(dir)

    return files


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=False,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""

    def execute_tool(description, *args, targets: List[str]):
        """Execute a checking tool with its arguments."""
        command_line = list(args)
        click.echo("{}: {}".format(description, " ".join(command_line)))
        rv = call(command_line + targets)
        if rv != 0:
            exit(rv)

    execute_tool("Formatting Files", "black", targets=["."])
    if fix_imports:
        execute_tool(
            "Fixing import order", "isort", "--profile", "black", targets=["."]
        )
    files = [
        f
        for f in (
            getfiles_paths("./app")
            + getfiles_paths("./migrations/versions")
            + ["./autoapp.py"]
        )
        if f.split(".")[-1] == "py"
    ]
    execute_tool("Checking code style", "flake8", targets=files)


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                full_pathname = os.path.join(dirpath, filename)
                click.echo("Removing {}".format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option("--url", default=None, help="Url to test (ex. /static/image.png)")
@click.option(
    "--order", default="rule", help="Property on Rule to order by (default: rule)"
)
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_headers = ("Rule", "Endpoint", "Arguments")

    if url:
        try:
            rule, arguments = current_app.url_map.bind("localhost").match(
                url, return_rule=True
            )
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(("<{}>".format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order)
        )
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ""
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += "{:" + str(max_rule_length) + "}"
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        max_endpoint_length = max_endpoint_length if max_endpoint_length > 8 else 8
        str_template += "  {:" + str(max_endpoint_length) + "}"
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = max_arguments_length if max_arguments_length > 9 else 9
        str_template += "  {:" + str(max_arguments_length) + "}"
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo("-" * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


def add_user_helper() -> "User":
    from app.apis.v1.users.models import User

    username = input("Username:").lower()
    while True:
        password = getpass("Password:")
        password_check = getpass("Type Password Again:")
        if password != password_check:
            print("Password & password check are not the same")
        else:
            break
    email = input("Email:").lower()
    while True:
        mobile = input("Mobile:")
        if not re.match(r"\+?\d*", mobile):
            print("Enter a valid mobile number")
            continue
        break

    first_name = input("First Name:").title()
    last_name = input("Last Name:").title()
    first_name_ar = input("First Name Ar:")
    last_name_ar = input("Last Name Ar:")

    return User(
        username=username,
        password=password,
        email=email,
        mobile=mobile,
        first_name=first_name,
        last_name=last_name,
        first_name_ar=first_name_ar,
        last_name_ar=last_name_ar,
    )


@click.command()
@click.argument("roles", nargs=-1)
@with_appcontext
def add_roles(roles: List[str]):
    """Add roles to be used with users."""
    from app.apis.v1.users.models import Role
    from app.database import db

    try:
        db.session.add_all([Role(role) for role in roles if not Role.get(name=role)])
        db.session.commit()
    except DatabaseError:
        print("Error adding roles")


@click.command()
@with_appcontext
def add_superuser():
    """Add Superuser."""
    from app.apis.v1.users.models import Role
    from app.database import db

    try:
        admin_role = Role.get(name="admin") or Role("admin")
        if not admin_role.id:
            db.session.add(admin_role)
            db.session.flush()
    except DatabaseError:
        print("Error finding or adding admin role")
        return False
    try:
        user = add_user_helper()
        db.session.add(user)
        db.session.commit()
        print("User added successfully.")
        user.add_roles(admin_role)
        db.session.commit()
    except DatabaseError:
        print("Error adding user")


@click.command()
@with_appcontext
def add_user():
    """Add User."""
    from app.apis.v1.users.models import Role
    from app.database import db

    try:
        user = add_user_helper()
        db.session.add(user)
        db.session.flush()
        roles_names = input("Roles(Comma separated):").split(",")
        roles = [
            role
            for role in [Role.get(name=role) for role in roles_names]
            if role is not None
        ]
        user.add_roles(roles)
        db.session.commit()
    except DatabaseError:
        print("Error adding user")


def register_commands(app: Flask) -> Flask:
    """Register Click commands."""
    app.cli.add_command(add_roles, "add-roles")
    app.cli.add_command(add_superuser, "add-superuser")
    app.cli.add_command(add_user, "add-user")
    app.cli.add_command(clean)
    app.cli.add_command(lint)
    app.cli.add_command(test)
    app.cli.add_command(urls)

    return app
