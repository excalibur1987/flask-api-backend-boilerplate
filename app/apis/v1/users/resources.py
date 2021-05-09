from typing import Dict, List

import werkzeug
from app.database import db
from app.exceptions import InvalidUsage
from app.utils import create_api, g
from app.utils.decorators import has_roles
from app.utils.file_storage import FileStorage
from app.utils.parsers import offset_parser
from flask import jsonify, request
from flask.helpers import make_response
from flask.wrappers import Response
from flask_jwt_extended import (
    current_user,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask_jwt_extended.utils import (
    create_access_token,
    get_csrf_token,
    get_jti,
    get_jwt,
)
from flask_principal import RoleNeed
from flask_restx import Resource, marshal
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import func

from .exceptions import UserExceptions
from .models import Session, User
from .parsers import user_info_parser, user_login_parser, user_parser
from .serializers import session_serializer, user_serializer
from .utils import extract_request_info

blueprint, api, ns = create_api(
    name="users",
    import_name=__name__,
    description="Users operations",
)

user_model = ns.model(
    "User",
    user_serializer,
)

session_model = ns.model("Session", session_serializer)

current_user: "User"


class UsersResource(Resource):
    @jwt_required()
    @ns.doc("get list of users")
    @ns.marshal_list_with(user_model, skip_none=True)
    def get(
        self,
    ):
        """Gets list of users"""

        return current_user

    @jwt_required()
    @ns.doc("Create new user")
    @ns.marshal_with(user_model)
    @ns.expect(user_parser)
    @has_roles("admin")
    def post(self):
        """Creates new user - requires admin permission-."""
        args = user_parser.parse_args()

        user = User(**args)

        return user


@ns.param("user_id", "user's id", type=int)
class UserResource(Resource):
    @jwt_required()
    @ns.doc("get user's info by id, or list of users")
    @ns.response(200, "user info model", model=user_model)
    @ns.marshal_with(user_model)
    def get(self, user_id: int = None):
        """Gets user's info"""
        user = User.get(id=user_id)

        return user

    @jwt_required()
    @ns.doc("update user's info")
    @ns.marshal_with(user_model)
    @ns.expect(user_info_parser)
    def put(self, user_id: int = None):
        """Updates user's info"""
        if user_id != current_user.id:
            raise InvalidUsage.user_not_authorized()
        args: Dict = user_info_parser.parse_args()

        newpwd = args.pop("newpwd")
        pwdcheck = args.pop("pwdcheck")

        current_user.set_password(newpwd=newpwd, pwdcheck=pwdcheck)

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
    @ns.doc("delete user's own account")
    @ns.expect(
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


class Login(Resource):
    @ns.doc("login user")
    @ns.response(200, "Successful login", model=user_model)
    @ns.response(404, "Invalid url")
    @ns.expect(user_login_parser)
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


@ns.param("user_id", "user's id", type=int)
@ns.param("slug", "session's slug", type=str)
class UserSession(Resource):
    @jwt_required()
    @ns.response(200, "User session", model=session_model)
    @ns.marshal_with(session_model)
    def get(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        return Session.get(slug=slug, user_id=user_id)

    @jwt_required()
    @ns.marshal_with(session_model)
    def delete(self, user_id: int, slug: str):
        if current_user.id != user_id and not g.identity.provides(RoleNeed("admin")):
            raise InvalidUsage.user_not_authorized()
        user_session = Session.get(slug=slug, user_id=user_id)
        user_session.delete(True)

        return


@ns.param("user_id", "user's id", type=int)
class UserSessions(Resource):
    @jwt_required()
    @ns.expect(offset_parser)
    @ns.serialize_multi(session_model, Session, description="User's Active Sessions")
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
    @ns.serialize_multi(session_model, Session, description="User's Active Sessions")
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


ns.add_resource(UsersResource, "/users/")
ns.add_resource(Login, "/users/login")
ns.add_resource(UserResource, "/users/<int:user_id>", endpoint="user")
ns.add_resource(
    UserSessions,
    "/users/<int:user_id>/sessions",
    endpoint="sessions",
)
ns.add_resource(
    UserSession,
    "/users/<int:user_id>/sessions/<slug>",
    endpoint="single_session",
)
