from typing import Dict, List

import werkzeug
from flask import jsonify, request
from flask.helpers import make_response
from flask.wrappers import Response
from flask_jwt_extended import current_user, jwt_required
from flask_jwt_extended.utils import (
    create_access_token,
    get_csrf_token,
    get_jti,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_principal import RoleNeed
from flask_restx import Resource, marshal
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func

from app.database import db
from app.exceptions import InvalidUsage, UserExceptions
from app.utils import g
from app.utils.decorators import has_roles
from app.utils.extended_objects import ExtendedNameSpace
from app.utils.file_storage import FileStorage
from app.utils.parsers import offset_parser

from .models import Session, User
from .parsers import user_info_parser, user_login_parser, user_parser
from .serializers import session_serializer, user_serializer
from .utils import extract_request_info

api = ExtendedNameSpace("users", description="Users operations")

user_model = api.model(
    "User",
    user_serializer,
)

session_model = api.model("Session", session_serializer)

current_user: "User"


class UsersResource(Resource):
    @jwt_required()
    @api.doc("get list of users")
    @api.marshal_list_with(user_model, skip_none=True)
    def get(
        self,
    ):
        """Gets list of users"""

        return current_user

    @jwt_required()
    @api.doc("Create new user")
    @api.marshal_with(user_model)
    @api.expect(user_parser)
    @has_roles("admin")
    def post(self):
        """Creates new user - requires admin permission-."""
        args = user_parser.parse_args()

        user = User(**args)
        user.save(True)
        return user


@api.param("user_id", "user's id", type=int)
class UserResource(Resource):
    @jwt_required()
    @api.doc("get user's info by id, or list of users")
    @api.response(200, "user info model", model=user_model)
    @api.marshal_with(user_model)
    def get(self, user_id: int = None):
        """Gets user's info"""
        user = User.get(id=user_id)

        return user

    @jwt_required()
    @api.doc("update user's info")
    @api.marshal_with(user_model)
    @api.expect(user_info_parser)
    def put(self, user_id: int = None):
        """Updates user's info"""
        if user_id != current_user.id:
            raise InvalidUsage.user_not_authorized()
        args: Dict = user_info_parser.parse_args()

        newpwd = args.pop("newpwd")
        pwdcheck = args.pop("pwdcheck")

        if newpwd:
            if newpwd != pwdcheck:
                raise UserExceptions.password_check_invalid()
            current_user.password = newpwd

        photo: werkzeug.datastructures.FileStorage = args.pop("photo")

        if photo:
            photostorage = FileStorage(data=photo.stream, name=photo.filename)
            photostorage.save()
            current_user.photo = photostorage.url

        for key, val in args.items():
            if hasattr(current_user, key) and val is not None:
                setattr(current_user, key, val)

        db.session.commit()

        return current_user

    @jwt_required()
    @api.doc("delete user's own account")
    @api.expect(
        user_login_parser.copy()
        .replace_argument(
            "username",
        )
        .add_argument(
            "confirm",
            type=bool,
            required=True,
            help="You must confirm deletion",
            location="form",
        )
    )
    def delete(self, user_id: int = None):
        """Deletes user's account permenantly"""
        args = user_login_parser.parse_args()
        user = User.get(id=user_id)

        if user_id != current_user.id:
            if g.identity.provides(RoleNeed("admin")):
                return self.admin_delete_user(user)
            raise InvalidUsage.user_not_authorized()
        if (
            user.username != args.get("username", None)
            or user.password != args.get("password", None)
            or not args.get("confirm", False)
        ):
            raise UserExceptions.wrong_login_creds()
        user.delete()
        response: Response = jsonify({"message": "User Account deleted succefully!"})
        unset_jwt_cookies(response)
        return response


class Logout(Resource):
    @api.doc("logout user and invalidate session")
    def get(self):

        active_session_token = get_jwt()["jti"]

        Session.get(token=active_session_token).delete(True)
        response: Response = jsonify({"message": "User logged out!"})
        response.delete_cookie("csrftoken")
        unset_jwt_cookies(response)

        return response


class Login(Resource):
    @api.doc("login user")
    @api.response(200, "Successful login", model=user_model)
    @api.response(404, "Invalid url")
    @api.expect(user_login_parser)
    def post(self):
        """User's login view"""
        args = user_login_parser.parse_args()
        user: User = User.query.filter(
            or_(
                func.lower(User.email) == args.get("username", "").lower(),
                func.lower(User.username) == args.get("username", "").lower(),
            )
        ).first()

        if not user or user.password != args.get("password", None):
            raise UserExceptions.wrong_login_creds()
        token = create_access_token(user)
        user.token = get_csrf_token(token)
        user_session = Session(
            user=user, token=get_jti(token), **extract_request_info(request=request)
        )
        user_session.save()
        response = make_response(
            marshal(
                user,
                user_model,
            )
        )
        set_access_cookies(response=response, encoded_access_token=token)
        return response


@api.param("user_id", "user's id", type=int)
@api.param("slug", "session's slug", type=str)
class UserSession(Resource):
    @jwt_required()
    @api.response(200, "User session", model=session_model)
    @api.marshal_with(session_model)
    def get(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        return Session.get(slug=slug, user_id=user_id)

    @jwt_required()
    @api.marshal_with(session_model)
    def delete(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        user_session = Session.get(slug=slug, user_id=user_id)
        user_session.delete(True)

        return


@api.param("user_id", "user's id", type=int)
class UserSessions(Resource):
    @jwt_required()
    @api.expect(offset_parser)
    @api.serialize_multi(session_model, Session, description="User's Active Sessions")
    def get(self, user_id: int = None):
        """Gets a list of user's active sessions"""
        args = offset_parser.parse_args()

        user_sessions = (
            Session.query.filter(
                Session.user_id == user_id,
            )
            .order_by(Session.id.asc())
            .offset(args.get("offset", 0))
            .limit(args.get("limit", 10))
            .all()
        )

        return user_sessions

    @jwt_required()
    @api.serialize_multi(session_model, Session, description="User's Active Sessions")
    def delete(self, user_id: int = None, slug: str = None):
        """Invalidates all users sessions except the current sessions"""
        user = User.get(id=user_id)

        if user.id != current_user.id and not g.identity.provides(RoleNeed("admin")):
            raise UserExceptions.wrong_login_creds()

        active_session_token = get_jwt()["jti"]

        user_sessions: List[Session] = Session.query.filter(
            Session.user_id == user.id
        ).all()
        for session_ in user_sessions:
            if session_.token != active_session_token:
                session_.delete(True)
        return [
            session_
            for session_ in user_sessions
            if session_.token == active_session_token
        ]


api.add_resource(UsersResource, "/")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(UserResource, "/<int:user_id>", endpoint="user")
api.add_resource(
    UserSessions,
    "/<int:user_id>/sessions",
    endpoint="sessions",
)
api.add_resource(
    UserSession,
    "/<int:user_id>/sessions/<slug>",
    endpoint="single_session",
)
