from typing import TYPE_CHECKING

from sqlalchemy.sql.schema import Column, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import INTEGER

from app.database import BaseModel

if TYPE_CHECKING:
    from app.apis.v1.roles.models._Role import Role

    from ._User import User


class UserRoles(BaseModel):
    __tablename__ = "user_roles"
    user_id = Column(INTEGER, nullable=False)
    role_id = Column(INTEGER, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            columns=["user_id"],
            refcolumns=["users.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            columns=["role_id"],
            refcolumns=["roles.id"],
            ondelete="CASCADE",
        ),
    )

    def __init__(self, user: "User", role: "Role") -> None:
        self.user_id = user.id
        self.role_id = role.id
