from typing import Any, List, TypedDict

from app.apis.v1.roles.models import Role
from app.apis.v1.users.models import User
from app.database import db
from flask.testing import FlaskClient
from werkzeug.http import parse_cookie


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


def create_user(user_info: UserDict):
    if User.get(username=user_info.get("username")):
        return

    role_names = user_info.get("roles")

    roles = [Role(role.lower(), f"{role.title()} Role") for role in role_names]

    user = User(**user_info)

    db.session.add_all(
        [
            user,
        ]
        + roles
    )

    db.session.flush()

    user.add_roles(roles)

    db.session.commit()


class ExtendedClient(FlaskClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        csrf = kwargs.pop("csrf")
        super().__init__(*args, **kwargs)
        self.csrf = csrf

    def open(self, *args, **kw):
        kw["headers"] = {**kw.get("headers", {}), **{"X-CSRF-TOKEN": self.csrf}}
        return super(ExtendedClient, self).open(*args, **kw)


def user_login(
    client: FlaskClient, user: UserDict = None, token: str = None
) -> ExtendedClient:

    if user:
        rv = client.post(
            "/v1/users/login",
            data=dict(username=user["username"], password=user["password"]),
        )
        token = rv.get_json().get("token")
        cookie = next(
            (
                cookie
                for cookie in rv.headers.getlist("Set-Cookie")
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

    return client
