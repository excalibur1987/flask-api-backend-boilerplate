import os
import random
import string
from datetime import timedelta
from typing import TypedDict

import pytz
from flask_principal import Permission, RoleNeed
from sqlalchemy.pool import NullPool


class RolesDict(TypedDict):
    user: Permission
    manager: Permission


class Config(object):
    FLASK_APP = os.getenv("FLASK_APP", "autoapp:app")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    TZ = pytz.timezone(os.getenv("TZ", "UTC"))
    SERVER_NAME = os.getenv("SERVER_NAME", None)
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "".join(
            random.choices(
                string.ascii_lowercase
                + string.ascii_uppercase
                + string.digits
                + string.printable,
                k=20,
            )
        ),
    )
    JWT_SECRET_KEY = os.getenv(
        "SECRET_KEY",
        SECRET_KEY,
    )
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_IDENTITY_CLAIM = "user"
    JWT_ERROR_MESSAGE_KEY = "error"
    JWT_COOKIE_SECURE = True
    ROLES: "RolesDict" = {
        "user": Permission(RoleNeed("user")),
        "manager": Permission(RoleNeed("manager")),
    }


class DevConfig(Config):

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60 * 60)
    SESSION_TYPE = "redis"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_ENV = "development"
    SECRET_KEY = "secretkey"


class ProdConfig(Config):

    PGSSLMODE = os.getenv("PGSSLMODE")
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=180)
    FLASK_ENV = "production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
