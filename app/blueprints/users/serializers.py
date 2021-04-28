from flask_restful import fields

role_serializer = {fields.String(attribute="name")}

user_serializer = {
    "id": fields.Integer,
    "userID": fields.String(attribute="user_id"),
    "name": fields.String,
    "active": fields.Boolean,
    "email": fields.String,
    "photo": fields.String,
    "mobile": fields.String,
    "roles": fields.List(fields.Nested(role_serializer)),
}
