from flask.app import Flask


def register_handlers(app: Flask) -> Flask:
    """A function to register global request handlers.
    To register a handler add them like the example
    Example usage:
        
        def fn(request: Request):
            pass

        app.before_request(fn)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """ 
    

    return app
