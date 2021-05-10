from flask import Flask

from app.apis.v1 import api_v1_bp


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
    app.register_blueprint(api_v1_bp)

    return app
