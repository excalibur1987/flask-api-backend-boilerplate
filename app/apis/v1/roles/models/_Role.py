from typing import TYPE_CHECKING, List

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

from app.database import BaseModel

if TYPE_CHECKING:
    from ...users.models import UserRoles


class Role(BaseModel):
    __tablename__ = "roles"
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, server_default="")

    users_roles: List["UserRoles"] = relationship(
        "UserRoles",
    )

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
