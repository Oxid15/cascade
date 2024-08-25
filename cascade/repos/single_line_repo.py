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

from typing import Any, Dict, List, Optional

from typing_extensions import Literal

from ..lines import Line
from .base_repo import BaseRepo


class SingleLineRepo(BaseRepo):
    def __init__(
        self,
        line: Line,
        *args: Any,
        meta_prefix: Optional[Dict[Any, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(line.get_root(), *args, meta_prefix=meta_prefix, **kwargs)
        self._lines = {line.get_root(): {"args": [], "kwargs": dict()}}
        self._line = line

    def __getitem__(self, key: str) -> Line:
        if key in self._lines:
            return self._line
        else:
            raise KeyError(
                f"The only line is {list(self._lines.keys())[0]}, {key} does not exist"
            )

    def __repr__(self) -> str:
        return f"SingleLine in {self._root}"

    def get_root(self) -> str:
        return self._root

    def reload(self) -> None:
        self._line.reload()

    def __len__(self) -> Literal[1]:
        return 1

    def get_line_names(self) -> List[str]:
        return [self._root]
