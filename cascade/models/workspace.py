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

import glob
import os
import warnings
from typing import Any, List, Literal, Union

from ..base import MetaHandler, PipeMeta, TraceableOnDisk
from ..models import ModelRepo


class Workspace(TraceableOnDisk):
    def __init__(
        self,
        path: str,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        default_repo: Union[str, None] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(path, meta_fmt, *args, **kwargs)
        self._root = path
        self._default = default_repo

        abs_root = os.path.abspath(self._root)
        dirs = sorted(
            [
                name
                for name in os.listdir(abs_root)
                if os.path.isdir(os.path.join(abs_root, name))
            ]
        )
        self._repo_names = []
        for d in dirs:
            meta_path = sorted(glob.glob(os.path.join(abs_root, d, "meta.*")))
            if len(meta_path) == 1:
                meta = MetaHandler.read(meta_path[0])
                if meta[0].get("type") == "repo":
                    self._repo_names.append(d)
            else:
                warnings.warn(f"Found {len(meta_path)} meta files in {d}")

        self._create_meta()

    def __getitem__(self, key: str) -> ModelRepo:
        if key in self._repo_names:
            return ModelRepo(os.path.join(self._root, key), log_history=False)
        else:
            raise KeyError(f"{key} repo does not exist in workspace {self._root}")

    def __len__(self) -> int:
        return len(self._repo_names)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["root"] = self._root
        meta[0]["len"] = len(self)
        meta[0]["type"] = "workspace"
        return meta

    def get_repo_names(self) -> List[str]:
        return self._repo_names

    def get_default(self) -> ModelRepo:
        if self._default is not None:
            return self[self._default]
        else:
            if len(self._repo_names) > 0:
                return self[self._repo_names[0]]
            else:
                raise RuntimeError("Tried to get the default repo when the workspace is empty")

    def set_default(self, repo: str) -> None:
        if repo in self._repo_names:
            self._default = repo
        else:
            raise KeyError(f"Repo {repo} does not exist in Workspace {self._root}")

    def reload(self) -> None:
        pass
