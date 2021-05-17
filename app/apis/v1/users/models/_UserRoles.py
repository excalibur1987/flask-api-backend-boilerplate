from typing import TYPE_CHECKING

from app.database import BaseModel
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import INTEGER

if TYPE_CHECKING:
    from app.apis.v1.roles.models._Role import Role

    from ._User import User


class UserRoles(BaseModel):
    """holds user roles pairs"""

    __tablename__ = "user_roles"
    user_id = Column(INTEGER, nullable=False, comment="user's table foreign key")
    role_id = Column(INTEGER, nullable=False, comment="role's table foreign key")

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

    def __init__(
        self, user: "User" = None, role: "Role" = None, user_id: int = None
    ) -> None:
        self.user_id = user_id or user.id
        self.role_id = role.id
