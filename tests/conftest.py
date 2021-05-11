import os
from typing import List, TypedDict

import pytest
from flask.testing import FlaskClient
from werkzeug.http import parse_cookie

from app import create_app
from app.database import db
from app.settings import TestConfig

from .helpers import ExtendedClient, create_user


class UserDict(TypedDict):
    username: str
    password: str
    password_check: str
    active: bool
    email: str
    photo: str
    mobile: str
    first_name: str
    last_name: str
    first_name_ar: str
    last_name_ar: str
    roles: List[str]


def get_test_app(DB_URI):
    """factory to return test app

    Args:
        DB_URI ([type]): database uri

    Returns:
        Flask instance: flask instance with test config
    """
    app = create_app(TestConfig)
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    return app


@pytest.fixture(scope="session")
def client(admin_user: UserDict, site_user: UserDict):
    DB_LOCATION = os.path.join(os.getcwd(), "tests", "test_db.db")
    DB_URI = f"sqlite:////{DB_LOCATION}"
    if not os.path.exists(DB_LOCATION):
        open(DB_LOCATION, "w")

    app = get_test_app(DB_URI)

    with app.test_client() as client:
        client: FlaskClient
        with app.app_context():
            db.create_all()
            for user in [admin_user, site_user]:
                create_user(user)
            yield client

    os.unlink(DB_LOCATION)


@pytest.fixture(scope="session")
def admin_client(admin_user: UserDict, site_user: UserDict):
    DB_LOCATION = os.path.join(os.getcwd(), "tests", "test_db.db")
    DB_URI = f"sqlite:////{DB_LOCATION}"
    if not os.path.exists(DB_LOCATION):
        open(DB_LOCATION, "w")

    app = get_test_app(DB_URI)

    with app.test_client() as client:
        client: ExtendedClient
        with app.app_context():
            db.create_all()
            users = {"admin": admin_user, "user": site_user}
            for user in users.values():
                create_user(user)
            response = client.post(
                "/v1/users/login",
                data=dict(
                    username=users["admin"]["username"],
                    password=users["admin"]["password"],
                ),
            )
            token = response.get_json().get("token")
            cookie = next(
                (
                    cookie
                    for cookie in response.headers.getlist("Set-Cookie")
                    if "access_token_cookie" in cookie
                ),
                None,
            )
            cookie_attrs = parse_cookie(cookie)

            client.set_cookie(
                server_name="/",
                key="access_token_cookie",
                httponly=True,
                secure=False,
                value=cookie_attrs["access_token_cookie"],
            )
            client.csrf = token
            client.__class__ = ExtendedClient
            yield client

    os.unlink(DB_LOCATION)


@pytest.fixture(scope="session")
def user_client(admin_user: UserDict, site_user: UserDict):
    DB_LOCATION = os.path.join(os.getcwd(), "tests", "test_db.db")
    DB_URI = f"sqlite:////{DB_LOCATION}"
    if not os.path.exists(DB_LOCATION):
        open(DB_LOCATION, "w")

    app = get_test_app(DB_URI)

    with app.test_client() as client:
        client: ExtendedClient
        with app.app_context():
            db.create_all()
            users = {"admin": admin_user, "user": site_user}
            for user in users.values():
                create_user(user)
            response = client.post(
                "/v1/users/login",
                data=dict(
                    username=users["user"]["username"],
                    password=users["user"]["password"],
                ),
            )
            token = response.get_json().get("token")
            cookie = next(
                (
                    cookie
                    for cookie in response.headers.getlist("Set-Cookie")
                    if "access_token_cookie" in cookie
                ),
                None,
            )
            cookie_attrs = parse_cookie(cookie)

            client.set_cookie(
                server_name="/",
                key="access_token_cookie",
                httponly=True,
                secure=False,
                value=cookie_attrs["access_token_cookie"],
            )
            client.csrf = token
            client.__class__ = ExtendedClient
            yield client

    os.unlink(DB_LOCATION)


@pytest.fixture(scope="session")
def admin_user() -> UserDict:
    return {
        "username": "admin_user",
        "password": "123456",
        "password_check": "123456",
        "email": "john.doe@example.com",
        "mobile": "+12345678910",
        "first_name": "john",
        "last_name": "doe",
        "roles": ["admin"],
    }


@pytest.fixture(scope="session")
def site_user() -> UserDict:
    return {
        "username": "test_user",
        "password": "123456",
        "password_check": "123456",
        "email": "jane.doe@example.com",
        "mobile": "+12345678910",
        "first_name": "jane",
        "last_name": "doe",
        "roles": ["user"],
    }
