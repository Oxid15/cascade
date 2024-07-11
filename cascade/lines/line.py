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

from abc import ABC, abstractmethod
from typing import Any

from ..base import Meta, Traceable


class Line(ABC, Traceable):
    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __getitem__(self, num: int) -> Any: ...

    @abstractmethod
    def reload(self): ...

    @abstractmethod
    def load(self, num: int) -> None: ...

    @abstractmethod
    def save(self, obj: Any, only_meta: bool = False) -> None: ...

    @abstractmethod
    def load_obj_meta(self, pathspec: str) -> Meta: ...

    @abstractmethod
    def get_root(self) -> str: ...

    def __repr__(self) -> str:
        return f"Line of {len(self)} of {self._item_cls}"
