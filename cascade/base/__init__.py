"""
Copyright 2022-2023 Ilia Moiseev

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

from typing import Union, List, Dict, Any

"""
Single Meta of basic object is just a dict, however Cascade supports
pipelines with lists of meta.

Do not use Meta when returning from `get_meta` methods! Use PipeMeta instead.
Meta type alias is designed for better readability and to explicitly state when the
variable is meta.
"""
Meta = Dict[Any, Any]

"""
This type is used when `get_meta` is called on any Traceable
"""
PipeMeta = List[Meta]

"""
This type described what we can get when reading previously written to meta object
"""
MetaFromFile = Union[List[Any], Dict[Any, Any]]


from .meta_handler import MetaHandler, supported_meta_formats
from .traceable import Traceable
from .meta_handler import CustomEncoder as JSONEncoder
from .history_logger import HistoryLogger
