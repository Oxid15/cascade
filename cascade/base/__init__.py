"""
# cascade.base

Core module of Cascade - contains basic objects and interfaces. Home for
`Traceable` class and other things that are not directly related to other
modules.

Copyright 2022-2024 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
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
from .history_handler import HistoryHandler
from .meta_handler import CustomEncoder as JSONEncoder
from .meta_handler import (MetaHandler, default_meta_format,
                           supported_meta_formats)
from .serialization import ObjectHandler
from .traceable import Traceable, TraceableOnDisk
