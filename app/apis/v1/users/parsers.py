import werkzeug
from flask_restx.reqparse import RequestParser

user_login_parser = RequestParser()
user_login_parser.add_argument(
    "username",
    type=str,
    required=True,
    help="You must provide username or email",
    location="form",
).add_argument(
    "password",
    type=str,
    required=True,
    help="You must provide a password",
    location="form",
)

user_delete_parser = user_login_parser.copy().add_argument(
    "confirm",
    type=bool,
    required=True,
    help="You must confirm deletion",
    location="form",
)

settings_parser = RequestParser()
settings_parser.add_argument(
    "pwd",
    dest="newpwd",
    type=str,
    default=None,
    location="form",
    required=False,
).add_argument(
    "pwdCheck",
    dest="pwdcheck",
    type=str,
    default=None,
    location="form",
    required=False,
).add_argument(
    "email",
    type=str,
    location="form",
    required=False,
).add_argument(
    "firstName",
    dest="first_name",
    type=str,
    location="form",
    required=False,
).add_argument(
    "lastName",
    dest="last_name",
    type=str,
    location="form",
    required=False,
).add_argument(
    "firstNameAr",
    dest="first_name_ar",
    type=str,
    location="form",
    required=False,
).add_argument(
    "lastNameAr",
    dest="last_name_ar",
    type=str,
    location="form",
).add_argument(
    "photo",
    default=None,
    type=werkzeug.datastructures.FileStorage,
    location="files",
)
