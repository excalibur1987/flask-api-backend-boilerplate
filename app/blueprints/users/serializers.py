from flask_restful import fields

role_serializer = {"name": fields.String}

user_serializer = {
    "id": fields.Integer,
    "username": fields.String(attribute="username"),
    "name": fields.String,
    "active": fields.Boolean,
    "email": fields.String,
    "photo": fields.String,
    "mobile": fields.String,
    "roles": fields.List(fields.String(attribute="name")),
}
