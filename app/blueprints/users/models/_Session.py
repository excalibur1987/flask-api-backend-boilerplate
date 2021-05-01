from datetime import datetime
from typing import TYPE_CHECKING

from app.database import BaseModel
from flask.globals import current_app
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER, TIMESTAMP, String

if TYPE_CHECKING:
    from ._User import User


class Session(BaseModel):
    __tablename__ = "sessions"

    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    active = Column(BOOLEAN, nullable=False, default=True)
    created_at = Column(
        TIMESTAMP(True),
        nullable=False,
        default=datetime.now(tz=current_app.config["TZ"]),
    )

    def __init__(
        self, user: "User", token: str, ip_address: str, platform: str, browser: str
    ) -> None:
        self.user_id = user.id
        self.token = token
        self.ip_address = ip_address
        self.platform = platform
        self.browser = browser