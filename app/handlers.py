from typing import TYPE_CHECKING

from flask.app import Flask
from flask_jwt_extended.exceptions import CSRFError
from flask_jwt_extended.jwt_manager import JWTManager
from flask_principal import (
    Identity,
    RoleNeed,
    UserNeed,
    identity_changed,
    identity_loaded,
)

from app.exceptions import InvalidUsage, UserExceptions

if TYPE_CHECKING:
    from app.apis.v1.users.models import User


def on_identity_loaded(sender, identity: int):

    pass


def jwt_handlers(jwt: JWTManager, app: Flask):
    def user_identity_lookup(user: "User"):
        return user.id

    def user_lookup_callback(_jwt_header, jwt_data):

        from app.apis.v1.users.models import Session, User

        session = Session.get(token=jwt_data["jti"], user_id=jwt_data["user"])
        if not session:
            raise InvalidUsage.invalid_session()
        user_id = jwt_data["user"]
        user = User.get(user_id)
        if not user or not user.active:
            raise InvalidUsage.user_not_authorized()
        identity = Identity(user_id)
        identity.provides.add(UserNeed(user_id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))
        identity_changed.send(app, identity=identity)

        return user

    def invalid_token_loader_callback(*args):

        return InvalidUsage.wrong_login_creds().to_json()

    jwt.user_identity_loader(user_identity_lookup)

    jwt.user_lookup_loader(user_lookup_callback)

    jwt.invalid_token_loader(invalid_token_loader_callback)


def invalid_error_handler(e: InvalidUsage):
    return e.to_json()


def invalid_csrf(e: CSRFError):
    raise UserExceptions.wrong_login_creds()


def register_handlers(app: Flask) -> Flask:
    """A function to register global request handlers.
    To register a handler add them like the example
    Example usage:

        def fn(request: Request):
            pass

        app.before_request(fn)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """
    identity_loaded.connect_via(app)(on_identity_loaded)

    app.errorhandler(InvalidUsage)(invalid_error_handler)
    app.errorhandler(CSRFError)

    return app
