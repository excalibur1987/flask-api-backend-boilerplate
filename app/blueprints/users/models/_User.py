from typing import TYPE_CHECKING, Any, List, Union

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BOOLEAN, String
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import BaseModel, db

if TYPE_CHECKING:
    from ._Role import Role  # NOQA


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
        "is_active", BOOLEAN(), nullable=False, server_default=text("1::bool")
    )

    password = Column(String, nullable=False, server_default="")

    # User identifiers
    email = Column(String, nullable=True)

    # meta data
    photo = Column(String, nullable=True)
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

    # Define the relationship to Role via UserRoles
    roles = relationship("Role", secondary="user_roles")
    token = ""

    def __init__(
        self,
        username: str,
        password: str,
        active: bool = True,
        email: str = None,
        photo: str = None,
        mobile: str = None,
        first_name: str = "",
        last_name: str = "",
        first_name_ar: str = "",
        last_name_ar: str = "",
    ) -> None:
        self.username = username
        self.password = generate_password_hash(password)
        self.active = active
        self.email = email
        self.photo = photo
        self.mobile = mobile
        self.first_name = first_name
        self.last_name = last_name
        self.first_name_ar = first_name_ar
        self.last_name_ar = last_name_ar

    def __setattr__(self, name, value):
        if name == "password":
            self.password = generate_password_hash(value)
        super(User, self).__setattr__(name, value)

    def __getattribute__(self, name: str) -> Any:
        if name == "password":
            return PasswordHelper(super(User, self).__getattribute__("password"))
        return super(User, self).__getattribute__(name)

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
