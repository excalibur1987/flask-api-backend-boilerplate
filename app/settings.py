import os
import random
import string
from datetime import timedelta

import pytz
from sqlalchemy.pool import NullPool


class Config(object):
    FLASK_APP = os.getenv("FLASK_APP", "autoapp:app")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = True
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
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE", "GET"]
    JWT_CSRF_IN_COOKIES = False


class DevConfig(Config):

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60 * 60)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_ENV = "development"
    SECRET_KEY = "secretkey"
    JWT_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False


class ProdConfig(Config):

    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=180)
    FLASK_ENV = "production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
