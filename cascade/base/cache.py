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
from typing import Any

from typing_extensions import Literal

from .serialization import ObjectHandler


class Cache:
    """
    General interface for object caching
    """
    def __init__(self, path: str, backend: Literal["pickle"] = "pickle") -> None:
        if not os.path.isdir(path):
            raise ValueError(f"path should be a folder, got {path}")
        os.makedirs(path, exist_ok=True)

        self.path = path
        self._handler = ObjectHandler(backend)

    def exists(self) -> bool:
        """
        Returns:
            bool: True if the object was already cached in this path
        """
        return len(os.listdir(self.path)) > 0

    def save(self, obj: Any) -> None:
        return self._handler.save(obj, self.path)

    def load(self) -> Any:
        return self._handler.load(self.path)
