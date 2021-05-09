from typing import Callable, TypeVar

from flask import Blueprint

from app.utils.extended_objectes import ExtendedApi


def create_api(name: str, description: str, import_name: str, url_prefix: str = ""):
    """A helper function to create blueprint, api and namespace instances

    Keyword arguments:
        name -- blueprint import name
        description -- description string passed to namespace instances
        import_name -- blueprint import name

    Returns:
        Returns A tuple of three instances
        - blueprint: the blueprint instance
        - api: flask_restx Api instance
        - ns: namespace instance
    """

    blueprint = Blueprint(name, import_name, url_prefix=url_prefix)

    api = ExtendedApi(
        blueprint,
        authorizations={
            "apikey": {"type": "apiKey", "in": "header", "name": "X-CSRF-TOKEN"}
        },
        security="apikey",
    )
    ns = api.namespace("", description=description)

    return blueprint, api, ns


T = TypeVar("T")


def chain(*functions: Callable[[T], T]) -> Callable[[T], T]:
    def returned_function(var: T) -> T:
        for func in functions:
            var = func(var)
        return var

    return returned_function
