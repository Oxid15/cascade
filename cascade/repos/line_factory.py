"""
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

from typing import Any

from typing_extensions import Literal

from ..base import MetaHandler
from ..lines import DataLine, Line, ModelLine


class LineFactory:
    # line is for repos before 0.14.0, which meant ModelLine
    _type2cls = {
        "line": ModelLine,
        "model_line": ModelLine,
        "data_line": DataLine,
        "model": ModelLine,
        "data": DataLine,
    }

    @classmethod
    def create(
        cls,
        path: str,
        *args: Any,
        line_type: Literal["model", "data", None] = None,
        **kwargs: Any,
    ) -> Line:
        if line_type not in cls._type2cls:
            raise TypeError(f"Cannot read a line from obj of type `{line_type}`")
        else:
            line_cls = cls._type2cls[line_type]
        line = line_cls(path, *args, **kwargs)
        return line

    @classmethod
    def read(cls, path: str, *args: Any, **kwargs: Any) -> Line:
        meta = MetaHandler.read_dir(path)
        obj_type = meta[0]["type"]

        if obj_type not in cls._type2cls:
            raise TypeError(f"Cannot read a line from obj of type `{obj_type}`")
        else:
            line = cls._type2cls[obj_type](path, *args, **kwargs)
            line.from_meta(meta)  # Is this OK?
            return line
