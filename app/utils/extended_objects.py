from functools import wraps
from typing import Callable, List, Union

from flask_restx import Model, OrderedModel, fields
from flask_restx.namespace import Namespace

from app.database import BaseModel

from .parsers import offset_parser


class ExtendedNameSpace(Namespace):
    def serialize_multi(
        self,
        restx_model: Union[Model, OrderedModel],
        db_model: BaseModel,
        description="",
    ):
        extended_model = self.model(
            f"{restx_model.name}s",
            {
                "count": fields.Integer(),
                "data": fields.Nested(restx_model, as_list=True),
                "limit": fields.Integer(),
                "offset": fields.Integer(),
            },
        )

        def wrapper(fn: Callable):
            @wraps(fn)
            @self.marshal_with(extended_model)
            @self.response(200, description, model=extended_model)
            def wrapped(*args, **kwargs):
                args_ = offset_parser.parse_args()
                result: List[BaseModel] = fn(*args, **kwargs)

                return {
                    "count": db_model.query.count(),
                    "limit": args_.get("limit", 10) or 10,
                    "offset": args_.get("offset", 0) or 0,
                    "data": result,
                }

            return wrapped

        return wrapper
