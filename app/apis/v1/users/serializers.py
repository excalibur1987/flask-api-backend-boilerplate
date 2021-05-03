from flask_restful import fields

role_serializer = {"name": fields.String}


user_serializer = {
    "id": fields.Integer,
    "username": fields.String(attribute="username"),
    "name": fields.String,
    "active": fields.Boolean,
    "email": fields.String,
    "photo": fields.String(attribute="photo.url"),
    "mobile": fields.String,
    "roles": fields.List(fields.String(attribute="name")),
}

session_serializer = {
    "id": fields.Integer(),
    "ipAddress": fields.String(attribute="ip_address"),
    "platform": fields.String(attribute="platform", default="N/A"),
    "browser": fields.String(attribute="browser", default="N/A"),
    "createdAt": fields.DateTime(attribute="created_at"),
}
