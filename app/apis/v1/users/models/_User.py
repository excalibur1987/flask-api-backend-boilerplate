import re
from typing import TYPE_CHECKING, List, Union

from app.database import BaseModel, db
from app.exceptions import UserExceptions
from app.utils.file_storage import FileStorage
from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BOOLEAN, String
from werkzeug.security import check_password_hash, generate_password_hash

if TYPE_CHECKING:
    from ...roles.models import Role
    from ._Session import Session

    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property


class PasswordHelper:
    password: str

    def __init__(self, password) -> None:
        self.password = password

    def __eq__(self, o: object) -> bool:
        equality: bool = check_password_hash(self.password, o)
        return equality


class User(BaseModel):
    __tablename__ = "users"
    username = Column(String, nullable=False)
    active = Column(
        "is_active", BOOLEAN(), nullable=False, server_default=cast(1, BOOLEAN)
    )

    _password = Column("password", String, nullable=False, server_default="")

    # User identifiers
    email = Column(String, nullable=True)

    # meta data
    _photo = Column("photo", String, nullable=True)
    mobile = Column(String, nullable=True)

    # User information
    first_name = Column(String, nullable=False, server_default="")
    last_name = Column(String, nullable=False, server_default="")

    first_name_ar = Column(String, nullable=False, server_default="")
    last_name_ar = Column(String, nullable=False, server_default="")

    # Uncomment to if you want to add manager employee relations
    # manager_id = Column(String, nullable=True)
    # manager: "User" = relationship(
    #     "User", foreign_keys=[manager_id], lazy=True, uselist=False
    # )

    # employees: List["User"] = relationship(
    #     "User",
    #     lazy=True,
    #     uselist=True,
    #     primaryjoin="User.user_id==foreign(User.manager_id)",
    # )

    # Relationships

    # Define the relationship to Role via UserRoles
    roles: List["Role"] = relationship("Role", secondary="user_roles")
    # user sessions
    sessions: List["Session"] = relationship(
        "Session", order_by="Session.created_at.asc()", uselist=True
    )

    token = None

    def __init__(
        self,
        username: str,
        password: str,
        password_check: str,
        active: bool = True,
        email: str = None,
        photo: str = None,
        mobile: str = None,
        first_name: str = "",
        last_name: str = "",
        first_name_ar: str = "",
        last_name_ar: str = "",
        **kwargs,
    ) -> None:
        if password != password_check:
            raise UserExceptions.password_check_invalid()
        self.username = username
        self._password = generate_password_hash(password)
        self.active = active
        self.email = email
        self._photo = photo
        self.mobile = mobile
        self.first_name = first_name
        self.last_name = last_name
        self.first_name_ar = first_name_ar
        self.last_name_ar = last_name_ar

    def set_password(self, newpwd: str, pwdcheck: str):
        regx = re.compile(current_app.config["PASSWORD_RULE"])
        if newpwd is None:
            return
        if newpwd != pwdcheck or not regx.match(newpwd):
            raise UserExceptions.password_check_invalid()
        self.password = generate_password_hash(newpwd)

    @hybrid_property
    def photo(self) -> FileStorage:
        return FileStorage(url=self._photo)

    @hybrid_property
    def password(self) -> PasswordHelper:
        return PasswordHelper(self._password)

    @hybrid_property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def name_ar(self) -> str:
        return f"{self.first_name_ar} {self.last_name_ar}"

    def check_password(self, pwd) -> bool:
        valid_password: bool = check_password_hash(self.password, pwd)
        return valid_password

    def add_roles(self, roles: Union[List["Role"], "Role"]):
        from ._UserRoles import UserRoles

        new_roles = [
            UserRoles(user=self, role=role)
            for role in (roles if isinstance(roles, list) else [roles])
        ]

        db.session.add_all(new_roles)

    def delete(self, persist=False):
        self.photo.delete()
        super().delete(persist=persist)
