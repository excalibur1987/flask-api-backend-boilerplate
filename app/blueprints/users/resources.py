from flask import Blueprint
from flask.helpers import make_response
from flask_jwt_extended import current_user, jwt_required, set_access_cookies
from flask_jwt_extended.utils import create_access_token, get_csrf_token
from flask_restful import Api, Resource, fields, marshal, marshal_with
from flask_restful.reqparse import RequestParser
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func

from app.exceptions import InvalidUsage
from app.utils.decorators import has_roles

from .models import User
from .serializers import user_serializer

blueprint = Blueprint("users", __name__, url_prefix="/api")


api = Api(blueprint)


class UserResource(Resource):
    parser = RequestParser()
    parser.add_argument(
        "password",
        type=str,
        required=True,
        help="You must provide a password",
        location=["form"],
    )
    parser.add_argument(
        "username",
        type=str,
        required=True,
        help="You must provide username or email",
        location=["form"],
    )

    @jwt_required()
    @marshal_with(user_serializer)
    def get(self, id=None):
        return User.get(id) if id else current_user

    def post(self):
        args = self.parser.parse_args()
        user: User = User.query.filter(
            or_(
                func.lower(User.email) == args.get("username", "").lower(),
                func.lower(User.username) == args.get("username", "").lower(),
            )
        ).first()

        if not user or user.password != args.get("password", None):
            raise InvalidUsage.wrong_login_creds()
        token = create_access_token(user)
        user.token = get_csrf_token(token)
        response = make_response(
            marshal(
                user,
                {
                    **user_serializer,
                    **{
                        "token": fields.String,
                    },
                },
            )
        )
        set_access_cookies(response=response, encoded_access_token=token)
        return response


class UsersResource(Resource):
    @jwt_required()
    @has_roles("admin")
    def get(self):
        return marshal(User.query.all(), user_serializer, envelope="users")


api.add_resource(UserResource, "/user", "/user/<int:id>")
api.add_resource(UsersResource, "/users")
