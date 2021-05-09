from typing import Dict
from urllib.parse import urlencode

from flask_restx.fields import Url, urlparse, urlunparse


class UrlWArgs(Url):

    query: Dict

    def __init__(
        self, endpoint=None, absolute=False, scheme=None, query: Dict = {}, **kwargs
    ):
        assert query is not None
        super().__init__(endpoint=endpoint, absolute=absolute, scheme=scheme, **kwargs)
        self.query = query

    def get_value(self, key, obj):
        if callable(key):
            return key(obj)
        if hasattr(obj, key):
            return getattr(obj, key)

        return key

    def output(self, key, obj, **kwargs):
        o = urlparse(super().output(key, obj, **kwargs))

        return urlunparse(
            (
                o.scheme,
                o.netloc,
                o.path,
                "",
                urlencode(
                    {k: self.get_value(val, obj) for k, val in self.query.items()}
                ),
                "",
            )
        )
