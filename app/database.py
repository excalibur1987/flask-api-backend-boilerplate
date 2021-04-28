from datetime import datetime
from typing import TYPE_CHECKING, Type, Union

from flask.globals import current_app
from flask_jwt_extended import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import Column, MetaData, and_, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql.schema import ForeignKey, MetaData
from sqlalchemy.sql.sqltypes import INTEGER, Boolean, DateTime, String

from app.exceptions import InvalidUsage

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)


db = SQLAlchemy(metadata=metadata)


class ExtendedModel(Model):
    id = Column(INTEGER, primary_key=True, nullable=False)

    def update(self, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs.get(key))
        if getattr(self, "updated_at"):
            self.updated_at = datetime.now(tz=current_app.config["TZ"])
        db.session.commit()

    @classmethod
    def get(cls, id=None, **kwargs):
        return (
            db.session.query(cls).get(id)
            if id
            else db.session.query(cls)
            .filter(and_(*[getattr(cls, arg) == val for arg, val in kwargs.items()]))
            .one_or_none()
        )

    def __iter__(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                yield key, getattr(self, key)


db = SQLAlchemy(model_class=ExtendedModel)


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
        from flask import session

        if not current_user and not kwargs.get("added_by", None):
            raise InvalidUsage.user_not_found()
        self.added_by = kwargs.get("added_by", current_user.id)


class CancelableModel(object):

    cancelled = Column(Boolean, nullable=False, server_default=text("false::boolean"))
    date_cancelled = Column(DateTime(True), nullable=True)

    @declared_attr
    def cancelled_by_id(cls):
        return Column(String, ForeignKey("user.id"))

    def cancel(self):

        if not current_user:
            raise InvalidUsage.user_not_found()
        self.cancelled = True
        self.cancelled_by_id = current_user.id
        self.date_cancelled = datetime.now()
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
