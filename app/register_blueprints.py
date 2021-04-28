from flask.app import Flask

from app.blueprints.users import blueprint as usr_bp


def register_blueprints(app: Flask) -> Flask:
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
    app.register_blueprint(usr_bp)

    return app
