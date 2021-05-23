import flask
from flask import Flask


def register_blueprints(app: "Flask") -> "Flask":
    """A function to register flask blueprint.
    To register blueprints add them like the example
    Example usage:
        from app.blueprints import blueprint
        app.register_blueprint(blueprint)
    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """

    # Monkey batch to solve this issue
    # https://github.com/flask-restful/flask-restful/pull/913
    flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
    from app.apis.v1 import api_v1_bp

    app.register_blueprint(api_v1_bp)

    return app
