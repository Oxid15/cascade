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
from typing import Any, Literal


class ObjectHandler(ABC):
    @abstractmethod
    def save(self, obj: Any, path: str) -> None:
        ...

    @abstractmethod
    def load(self, path: str) -> Any:
        ...


class Pickler(ObjectHandler):
    def load(self, path: str) -> Any:
        with open(path, "rb") as f:
            return pickle.load(f)

    def save(self, obj: Any, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump(obj, f)


class Cache:
    def __init__(self, path: str, backend: Literal["pickle"] = "pickle") -> None:
        self.path = path
        if backend == "pickle":
            self._handler = Pickler()
        else:
            raise ValueError(f"{backend} is not in (pickle,)")

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def save(self, obj: Any) -> None:
        return self._handler.save(obj, self.path)

    def load(self) -> Any:
        return self._handler.load(self.path)
