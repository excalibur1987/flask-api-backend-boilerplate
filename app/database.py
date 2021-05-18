from datetime import datetime
from typing import TYPE_CHECKING, Type, TypeVar, Union

from flask.globals import current_app
from flask_jwt_extended import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import Column, and_, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql.expression import cast, or_
from sqlalchemy.sql.schema import ForeignKey, MetaData, Table
from sqlalchemy.sql.sqltypes import BOOLEAN, INTEGER, Boolean, DateTime, String

from app.exceptions import InvalidUsage

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

T = TypeVar("T")


class ExtendedModel(Model):
    __table__: Table
    __tablename__: str
    id = Column(
        INTEGER, primary_key=True, nullable=False, comment="Unique row identifier"
    )
    updated_at: "Column[datetime]"

    def update(self, ignore_none: bool = False, **kwargs):
        for key in kwargs.keys():
            if not ignore_none or kwargs.get(key) is not None:
                setattr(self, key, kwargs.get(key))
        if hasattr(self, "updated_at"):
            self.updated_at = datetime.now(tz=current_app.config["TZ"])
        db.session.commit()

    @classmethod
    def get(cls: T, id: int = None, **kwargs) -> Union[T, None]:
        """Gets class instance using id or named attributes
        Args:
            id (int, optional): User id.
            kwargs: named arguments must be an attribute of the class
        Returns:
            An instance of the class
        """
        for arg in kwargs.keys():
            assert hasattr(cls, arg)
        return (
            db.session.query(cls)
            .filter(
                and_(
                    or_(getattr(cls, "id") == id, id == None),
                    *[
                        getattr(cls, arg) == val
                        for arg, val in kwargs.items()
                        if hasattr(cls, arg)
                    ],
                )
            )
            .one_or_none()
        )

    def __iter__(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                yield key, getattr(self, key)

    def save(self, persist=True):
        """Saves instance to database

        Args:
            persist (bool, optional): Commit changes. Defaults to True.
        """
        db.session.add(self)
        if persist:
            db.session.commit()

    def delete(self, persist=False):
        """Deletes instance from database

        Args:
            persist (bool, optional): Commit changes. Defaults to False.
        """
        db.session.delete(self)
        if persist:
            db.session.commit()


db = SQLAlchemy(model_class=ExtendedModel, metadata=metadata)


class ViewModel(object):
    __table_args__ = {"info": dict(is_view=True)}
    is_view = True

    @classmethod
    def get_ddl(cls):
        sql = "select pg_get_viewdef(to_regclass(:view))"
        return (
            "CREATE OR REPLACE VIEW public.v_user_view\nAS\n"
            + f"{db.session.execute(sql, params={'view':cls.__tablename__}).scalar()}"
        )

    def delete(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model

    BaseModel: Type[ExtendedModel] = db.make_declarative_base(ExtendedModel)
else:
    BaseModel = db.Model


class DatedModel(object):

    date_added = Column(DateTime(True), nullable=False, server_default=text("now()"))
    date_updated = Column(DateTime(True), nullable=False, server_default=text("now()"))

    @declared_attr
    def added_by(cls):
        return Column(String, ForeignKey("user.id"))

    def __init__(self, **kwargs) -> None:

        if not current_user and not kwargs.get("added_by", None):
            raise InvalidUsage.user_not_found()
        self.added_by = kwargs.get("added_by", current_user.id)


class CancelableModel(object):

    cancelled = Column(Boolean, nullable=False, server_default=cast(0, BOOLEAN))
    date_cancelled = Column(DateTime(True), nullable=True)

    @declared_attr
    def cancelled_by_id(cls):
        return Column(String, ForeignKey("user.id"))

    def cancel(self):

        if not current_user:
            raise InvalidUsage.user_not_found()
        self.cancelled = True
        self.cancelled_by_id = current_user.id
        self.date_cancelled = datetime.now(tz=current_app.config["TZ"])
        db.session.commit()


def ArrayList(_type, dimensions=1):
    # https://stackoverflow.com/a/29859182
    class MutableList(Mutable, list):
        @classmethod
        def coerce(cls, key, value):
            if not isinstance(value, cls):
                return cls(value)
            else:
                return value

    def _make_mm(mmname):
        def mm(self, *args, **kwargs):
            try:
                retval = getattr(list, mmname)(self, *args, **kwargs)
            finally:
                self.changed()
            return retval

        return mm

    modmethods = [
        "append",
        "clear",
        "copy",
        "count",
        "extend",
        "index",
        "insert",
        "pop",
        "remove",
        "reverse",
        "sort",
    ]

    for m in modmethods:
        setattr(MutableList, m, _make_mm(m))

    return MutableList.as_mutable(ARRAY(_type, dimensions=dimensions))
