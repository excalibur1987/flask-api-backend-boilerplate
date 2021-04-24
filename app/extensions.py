from flask.app import Flask


def register_extensions(app: Flask) -> Flask:
    """A function to register flask extension.
    To register extensions add them like the example
    Example usage:
        cors = Cors()
        cors.init_app(app)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """    
    return app
