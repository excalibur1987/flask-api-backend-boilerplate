import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from app.database import BaseModel
from flask.globals import current_app
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER, TIMESTAMP, String

if TYPE_CHECKING:
    from ._User import User


class Session(BaseModel):
    """table for user's active sessions"""

    __tablename__ = "sessions"

    user_id = Column(
        INTEGER,
        ForeignKey("users.id"),
        nullable=False,
        comment="user's table foreign key",
    )
    token = Column(String, nullable=False, comment="session's token")
    ip_address = Column(String, nullable=True, comment="machine's ip address")
    platform = Column(String, nullable=True, comment="machine's os platform")
    browser = Column(String, nullable=True, comment="registered browser")
    active = Column(BOOLEAN, nullable=False, default=True)
    slug = Column(
        String, nullable=False, unique=True, comment="unique's slug identifier"
    )
    created_at = Column(
        TIMESTAMP(True), nullable=False, comment="session's creation date"
    )

    def __init__(
        self, user: "User", token: str, ip_address: str, platform: str, browser: str
    ) -> None:
        self.user_id = user.id
        self.token = token
        self.ip_address = ip_address
        self.platform = platform
        self.browser = browser
        self.slug = str(uuid.uuid4())
        self.created_at = datetime.now(tz=current_app.config["TZ"])
