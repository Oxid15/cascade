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
import warnings
from typing import Any, Iterator, List, Optional

from typing_extensions import Literal

from ..base import Meta, MetaHandler, MetaIOError, TraceableOnDisk
from ..data import T
from ..repos.repo import Repo


class Workspace(TraceableOnDisk):
    def __init__(
        self,
        path: str,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        default_repo: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(path, meta_fmt, *args, **kwargs)
        self._default = default_repo

        os.makedirs(self._root, exist_ok=True)

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
            try:
                meta = MetaHandler.read_dir(os.path.join(abs_root, d))
                if meta[0].get("type") == "repo":
                    self._repo_names.append(d)
            except MetaIOError as e:
                warnings.warn(str(e))

        self.sync_meta()

    def __getitem__(self, key: str) -> Repo:
        if key in self._repo_names:
            return Repo(os.path.join(self._root, key))
        else:
            raise KeyError(f"{key} repo does not exist in workspace {self._root}")

    def __len__(self) -> int:
        return len(self._repo_names)

    def __iter__(self) -> Iterator[T]:
        for repo in self._repo_names:
            yield self.__getitem__(repo)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["root"] = self._root
        meta[0]["len"] = len(self)
        meta[0]["type"] = "workspace"
        return meta

    def get_repo_names(self) -> List[str]:
        return self._repo_names

    def get_default(self) -> Repo:
        if self._default is not None:
            return self[self._default]
        else:
            if len(self._repo_names) > 0:
                return self[self._repo_names[0]]
            else:
                raise RuntimeError(
                    "Tried to get the default repo when the workspace is empty"
                )

    def set_default(self, repo: str) -> None:
        if repo in self._repo_names:
            self._default = repo
        else:
            raise KeyError(f"Repo {repo} does not exist in Workspace {self._root}")

    def reload(self) -> None:
        pass

    def load_obj_meta(self, model: str) -> Meta:
        """
        Loads metadata of a model from disk

        Parameters
        ----------
        model : str
            model slug e.g. `fair_squid_of_bliss`

        Returns
        -------
        Meta
            Model metadata

        Raises
        ------
        FileNotFoundError
            Raises if failed to find the model with slug specified
        """

        for repo_name in self._repo_names:
            try:
                repo = Repo(os.path.join(self._root, repo_name))
                meta = repo.load_obj_meta(model)
            except FileNotFoundError:
                continue
            else:
                return meta
        raise FileNotFoundError(
            f"Failed to find the model {model} in the workspace at {self._root}"
        )

    def add_repo(self, name: str, *args: Any, **kwargs: Any) -> Repo:
        """
        Creates and adds repo to the Workspace

        Parameters
        ----------
        name : str
            Name of the repo

        Returns
        -------
        Repo
            Created repo

        Raises
        ------
        ValueError
            If the repo already exists
        """
        repo = Repo(os.path.join(self._root, name), *args, **kwargs)
        if name not in self._repo_names:
            self._repo_names.append(name)

        self.sync_meta()
        return repo
