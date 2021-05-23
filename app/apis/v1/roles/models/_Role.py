from app.database import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String


class Role(BaseModel):
    """contains basic roles for the aplication"""

    __tablename__ = "roles"
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, server_default="")

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
