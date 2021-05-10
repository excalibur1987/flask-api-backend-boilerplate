from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String

from app.database import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, server_default="")

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
