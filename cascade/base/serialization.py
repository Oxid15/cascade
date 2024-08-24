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

import os
import pickle
from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import Literal


class BaseObjectHandler(ABC):
    @abstractmethod
    def save(self, obj: Any, path: str) -> None:
        ...

    @abstractmethod
    def load(self, path: str) -> Any:
        ...


class Pickler(BaseObjectHandler):
    def load(self, path: str) -> Any:
        with open(os.path.join(path, "object.pkl"), "rb") as f:
            return pickle.load(f)

    def save(self, obj: Any, path: str) -> None:
        with open(os.path.join(path, "object.pkl"), "wb") as f:
            pickle.dump(obj, f)


class ObjectHandler(BaseObjectHandler):
    """
    Universal serializer interface. Can be supported by
    interchangeable backends.
    """
    def __init__(self, backend: Literal["pickle"] = "pickle") -> None:
        if backend == "pickle":
            self._handler = Pickler()
        else:
            raise ValueError(f"{backend} is not in (pickle,)")

    def save(self, obj: Any, path: str) -> None:
        return self._handler.save(obj, path)

    def load(self, path: str) -> Any:
        return self._handler.load(path)
