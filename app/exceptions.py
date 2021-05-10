from flask import jsonify


def template(
    data,
    code=500,
):
    return {"errors": data, "status_code": code}


USER_NOT_FOUND = template(["User not found"], code=404)
UNKNOWN_ERROR = template([], code=500)
USER_NOT_AUTHORIZED = template(["Unauthorized access"], code=401)
INVALID_SESSION = template(["Invalid login session, please re-login"], code=401)
EMPTY_MISSING_FILE = template(["File is empty or not uploaded correctly"], code=400)
SIZE_LIMIT_EXCEEDED = template(["File size is larger than 1MB"], code=400)
UNSUPPORTED_FORMAT = template(["Unsupported file format"], code=415)
INVALID_SEARCH_PARAMS = template("No data available to fit your search", code=404)


class InvalidUsage(Exception):
    status_code = 500

    def __init__(self, errors, status_code=None, payload=None):
        Exception.__init__(self)
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = {
            "errors": self.errors,
        }
        return jsonify(rv), self.status_code

    @classmethod
    def custom_error(cls, message, code=500):
        return cls(**template([message], code))

    @classmethod
    def invalid_session(cls):
        return cls(**INVALID_SESSION)

    @classmethod
    def user_not_found(cls):
        return cls(**USER_NOT_FOUND)

    @classmethod
    def user_not_authorized(cls):
        return cls(**USER_NOT_AUTHORIZED)

    @classmethod
    def unknown_error(cls):
        return cls(**UNKNOWN_ERROR)

    @classmethod
    def empty_missing_file(cls):
        return cls(**EMPTY_MISSING_FILE)

    @classmethod
    def unsupported_format(cls):
        return cls(**UNSUPPORTED_FORMAT)

    @classmethod
    def size_limit_exceeded(cls):
        return cls(**SIZE_LIMIT_EXCEEDED)

    @classmethod
    def invalid_search_params(cls):
        return cls(**INVALID_SEARCH_PARAMS)


class CommonExcelExc(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


WRONG_LOGIN_CREDS = template(["Username or password are not correct"], code=404)
USER_ALREADY_REGISTERED = template(["User already registered"], code=422)
PASSWORD_CHECK_INVALID = template(
    ["Password and password check must be equal."], code=400
)


class UserExceptions(Exception):
    status_code = 500

    def __init__(self, errors, status_code=None, payload=None):
        Exception.__init__(self)
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = {
            "errors": self.errors,
        }
        return jsonify(rv), self.status_code

    @classmethod
    def user_already_registered(cls):
        return cls(**USER_ALREADY_REGISTERED)

    @classmethod
    def wrong_login_creds(cls):
        return cls(**WRONG_LOGIN_CREDS)

    @classmethod
    def password_check_invalid(cls):
        return cls(**PASSWORD_CHECK_INVALID)
