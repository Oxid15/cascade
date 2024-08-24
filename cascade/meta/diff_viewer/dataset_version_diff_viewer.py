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

from ...base import MetaHandler
from .base_diff_viewer import BaseDiffViewer


class DatasetVersionDiffViewer(BaseDiffViewer):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self._default_depth = 9
        self._default_diff_depth = 8

    def _read_objects(self, path: str) -> Dict[str, Any]:
        self._check_path(path, "version_history")

        versions = MetaHandler.read(path)["versions"]

        version_dict = {}
        for pipe_key in versions:
            for meta_key in versions[pipe_key]:
                version_dict.update(
                    {
                        versions[pipe_key][meta_key]["version"]: versions[pipe_key][
                            meta_key
                        ]
                    }
                )
        return {key: version_dict[key] for key in sorted(version_dict.keys())}
