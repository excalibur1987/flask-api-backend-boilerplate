from flask import g
from flask_principal import Identity

from .decorators import has_roles
from .extended_objects import ExtendedNameSpace
from .file_storage import FileStorage
from .helpers import chain
from .url_w_args import UrlWArgs


class GlobalObject(object):
    identity: Identity


g: GlobalObject
