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

from typing import Any, Dict

from ...base import HistoryHandler
from .base_diff_viewer import BaseDiffViewer


class HistoryDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 2
        self._default_diff_depth = 1

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, ("history",))

        hl = HistoryHandler(path)

        states = {str(i): hl.get(i) for i in range(len(hl))}
        return states
