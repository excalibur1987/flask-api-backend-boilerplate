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


user_info_parser = RequestParser()
user_info_parser.add_argument(
    "pwd",
    dest="password",
    type=str,
    default=None,
    location="form",
    required=False,
).add_argument(
    "pwdCheck",
    dest="password_check",
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
    "mobile",
    dest="mobile",
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

user_parser = user_info_parser.copy().add_argument(
    "username",
    dest="username",
    type=str,
    location="form",
)

user_query_parser = RequestParser()
user_query_parser.add_argument(
    "q", choices=["sessions"], type=str, location="args", required=False
)
user_query_parser.add_argument(
    "slug", help="session's identifying", type=str, location="args", required=False
)
