import os
from typing import List, TypedDict

import pytest
from flask.app import Flask
from flask.testing import FlaskClient

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


@pytest.fixture()
def db_location():
    loc = os.path.join(os.getcwd(), "tests", "test_db.db")
    if not os.path.exists(loc):
        open(loc, "w")
    yield loc
    os.unlink(loc)


@pytest.fixture()
def db_uri(db_location):
    return f"sqlite:////{db_location}"


@pytest.fixture()
def test_app(db_uri: str):
    """factory to return test app

    Args:
        db_uri ([type]): database uri

    Returns:
        Flask instance: flask instance with test config
    """
    app = create_app(TestConfig)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    return app


@pytest.fixture()
def client(admin_user: UserDict, site_user: UserDict, test_app: Flask):
    users = {"admin": admin_user, "user": site_user}

    with test_app.test_client() as client:
        client: FlaskClient
        with test_app.app_context():
            db.create_all()
            for user in [admin_user, site_user]:
                create_user(user)

            def login_client(user: str = None):
                if user is not None:
                    response = client.post(
                        "/v1/users/login",
                        data=dict(
                            username=users["admin"]["username"],
                            password=users["admin"]["password"],
                        ),
                    )
                    token = response.get_json().get("token")
                    client.csrf = token
                    client.__class__ = ExtendedClient
                return client

            return login_client


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
