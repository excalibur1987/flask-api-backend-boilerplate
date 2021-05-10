from typing import Any, TypedDict

from flask.testing import FlaskClient

from app.apis.v1.roles.models import Role
from app.apis.v1.users.models import User, UserRoles
from app.database import db


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


class USERS(object):
    ADMIN: UserDict = {
        "username": "admin_user",
        "password": "123456",
        "password_check": "123456",
        "email": "john.doe@example.com",
        "mobile": "+12345678910",
        "first_name": "john",
        "last_name": "doe",
    }
    USER: UserDict = {
        "username": "test_user",
        "password": "123456",
        "password_check": "123456",
        "email": "jane.doe@example.com",
        "mobile": "+12345678910",
        "first_name": "jane",
        "last_name": "doe",
    }

    @classmethod
    def create_admin(cls):
        user = User(**cls.ADMIN)

        admin_role = Role("admin", "Admin Role")

        db.session.add_all([user, admin_role])

        db.session.flush()

        db.session.add(UserRoles(user=user, role=admin_role))

        db.session.commit()

    @classmethod
    def create_user(cls):
        user = User(**cls.USER)

        user_role = Role("user", "User Role")

        db.session.add_all([user, user_role])

        db.session.flush()

        db.session.add(UserRoles(user=user, role=user_role))

        db.session.commit()


class ExtendedClient(FlaskClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        csrf = kwargs.pop("csrf")
        super().__init__(*args, **kwargs)
        self.csrf = csrf

    def open(self, *args, **kw):
        kw["headers"].update("X-CSRF-TOKEN", self.csrf)
        return super(ExtendedClient, self).open(*args, **kw)


def admin_login(client: FlaskClient):

    USERS.create_admin()

    rv = client.post(
        "/v1/users/login",
        data=dict(username=USERS.ADMIN["username"], password=USERS.ADMIN["password"]),
    )

    csrf_token = rv.get_json().get("token")

    client.__class__ = ExtendedClient

    client.csrf = csrf_token

    return client


def user_login(client: FlaskClient):
    USERS.create_user()
    rv = client.post(
        "/v1/users/login",
        data=dict(username=USERS.USER["username"], password=USERS.ADMIN["password"]),
    )

    csrf_token = rv.get_json().get("token")

    client.__class__ = ExtendedClient

    client.csrf = csrf_token

    return client
