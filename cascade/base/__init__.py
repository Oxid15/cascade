"""
cascade.base
============

Core module of Cascade - contains basic objects and interfaces. Home for
``Traceable`` class and other things that are not directly related to other
modules.
"""

from typing import Any, Dict, List, NoReturn

"""
Single meta of basic object is just a dict, however Cascade works with
pipelines with lists of meta. This is why default meta is a list.

This type is used when ``get_meta`` is called on any Traceable
"""
MetaBlock = Dict[Any, Any]
Meta = List[MetaBlock]


class MetaIOError(IOError):
    pass


class ZeroMetaError(MetaIOError):
    pass


class MultipleMetaError(MetaIOError):
    pass


def raise_not_implemented(class_name: str, name: str) -> NoReturn:
    raise NotImplementedError(
        f"Default {class_name} class '{name}()' "
        f"method called. May be you haven't "
        f"implemented it in the successor class"
    )


from .cache import Cache
from .config import Config
from .meta_handler import CustomEncoder as JSONEncoder
from .meta_handler import MetaHandler, default_meta_format, supported_meta_formats
from .serialization import ObjectHandler
from .traceable import Traceable, TraceableOnDisk

__all__ = [
    "Cache",
    "Config",
    "JSONEncoder",
    "MetaHandler",
    "ObjectHandler",
    "Traceable",
    "TraceableOnDisk",
    "default_meta_format",
    "supported_meta_formats",
    "raise_not_implemented",
    "MetaBlock",
    "Meta",
    "MetaIOError",
    "ZeroMetaError",
    "MultipleMetaError",
]
