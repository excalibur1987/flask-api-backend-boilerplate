from flask import Blueprint, request
from flask.helpers import make_response
from flask_jwt_extended import current_user, jwt_required, set_access_cookies
from flask_jwt_extended.utils import create_access_token, get_csrf_token, get_jti
from flask_restful import Api, Resource, fields, marshal, marshal_with
from flask_restful.reqparse import RequestParser
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func

from app.blueprints.users.utils import extract_request_info
from app.exceptions import InvalidUsage
from app.utils.decorators import has_roles

from .models import Session, User
from .serializers import user_serializer

blueprint = Blueprint("users", __name__, url_prefix="/api")


api = Api(blueprint)


current_user: "User"


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
        user_session = Session(
            user=user, token=get_jti(token), **extract_request_info(request=request)
        )
        user_session.save()
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


class UserSssions(Resource):
    parser = RequestParser()
    parser.add_argument(
        "id",
        type=int,
        required=True,
        help="You must provide a valid id",
        location=["form"],
    )

    @jwt_required()
    @marshal_with(
        {
            "id": fields.Integer(),
            "ipAddress": fields.String(attribute="ip_address"),
            "platform": fields.String(attribute="platform", default="N/A"),
            "browser": fields.String(attribute="browser", default="N/A"),
            "createdAt": fields.DateTime(attribute="created_at"),
        }
    )
    def get(self):
        sessions = current_user.sessions
        return sessions

    @jwt_required()
    def delete(self):
        """Delete User session by providing id

        Returns:
            [type]: [description]
        """
        args = self.parser.parse_args()
        user_session = Session.get(id=args["id"], user_id=current_user.id)
        if user_session:
            user_session.delete(True)
        return {"message": "Session deleted successfully."}


class UsersResource(Resource):
    @jwt_required()
    @has_roles("admin")
    def get(self):
        return marshal(User.query.all(), user_serializer, envelope="users")


api.add_resource(UserResource, "/user", "/user/<int:id>")
api.add_resource(UsersResource, "/users")
api.add_resource(UserSssions, "/user/sessions", "/user/session")
