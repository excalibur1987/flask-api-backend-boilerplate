from flask.app import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_principal import Principal

from app.database import db
from app.handlers import jwt_handlers

jwt = JWTManager()
migrate = Migrate()
principal = Principal()


def register_extensions(app: Flask) -> Flask:
    """A function to register flask extension.
    To register extensions add them like the example
    Example usage:
        cors = Cors()
        cors.init_app(app)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """

    db.init_app(app)

    migrate.init_app(app, db)

    # Configure flask_principal
    principal.init_app(app)

    # Configure JWT and its loaders
    jwt.init_app(app)

    jwt_handlers(jwt, app)

    return app
