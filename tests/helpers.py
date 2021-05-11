from typing import Any, List, TypedDict

from flask.testing import FlaskClient

from app.apis.v1.roles.models import Role
from app.apis.v1.users.models import User
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
