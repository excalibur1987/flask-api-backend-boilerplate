from typing import Dict

import werkzeug
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
from flask_restx import Resource, marshal
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import func

from app.database import db
from app.utils import create_api
from app.utils.decorators import has_roles
from app.utils.file_storage import FileStorage

from .exceptions import UserExceptions
from .models import Session, User
from .parsers import settings_parser, user_delete_parser, user_login_parser
from .serializers import session_serializer, user_serializer
from .utils import extract_request_info

blueprint, api, ns = create_api(
    name="users", import_name=__name__, description="Users operations"
)

user_model = api.model(
    "User",
    user_serializer,
)

session_model = api.model("Sessions", session_serializer)

current_user: "User"


class UserResource(Resource):
    @jwt_required()
    @ns.doc("get user's info by id, or current user's")
    @ns.marshal_with(user_model, skip_none=True)
    def get(self):
        """Gets current user's info"""

        return current_user

    @jwt_required()
    @ns.doc("delete user's own account")
    @ns.expect(user_delete_parser)
    def delete(self):
        """Delets user's account permenantly"""
        args = user_login_parser.parse_args()

        if (
            current_user.username != args.get("username", None)
            or current_user.password != args.get("password", None)
            or not args.get("confirm", False)
        ):
            raise UserExceptions.wrong_login_creds()
        current_user.delete()
        response: Response = jsonify({"message": "User Account deleted succefully!"})
        unset_jwt_cookies(response)
        return response

    @ns.doc("login user")
    @ns.response(200, "Successful login", model=user_model)
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


class UserSettings(Resource):
    @jwt_required()
    @ns.doc("update user's info")
    @ns.marshal_with(user_model)
    @ns.expect(settings_parser)
    def put(self):
        """Updates user's info"""
        args: Dict = settings_parser.parse_args()

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


class UserSessions(Resource):
    @jwt_required()
    @ns.doc("get user's active sessions")
    @ns.marshal_list_with(session_model)
    def get(self, slug: str = None):
        """Gets a list of user's active sessions"""

        sessions = Session.get(slug=slug) or current_user.sessions
        return sessions

    @jwt_required()
    @ns.marshal_list_with(session_model)
    def delete(self, slug: str = None):
        """Invalidates all users sessions except the current sessions"""

        active_session_token = get_jwt()["jti"]

        user_sessions = Session.query.filter(
            or_(
                and_(
                    Session.user_id == current_user.id,
                    Session.token != active_session_token,
                    slug != None,
                ),
                Session.slug == slug,
            )
        ).all()
        for session_ in user_sessions:
            session_.delete(True)
        return current_user.sessions


class UsersResource(Resource):
    @jwt_required()
    @ns.marshal_list_with(user_model, envelope="users")
    @ns.doc("Gets a list of active users")
    @has_roles("admin")
    def get(self):
        """Gets a list of active users"""
        return User.query.filter(User.active).all()


ns.add_resource(UserResource, "/user")
ns.add_resource(UserSettings, "/user/settings")
ns.add_resource(UsersResource, "/users")
ns.add_resource(
    UserSessions, "/user/sessions", "/user/sessions/<slug>", endpoint="sessions"
)
