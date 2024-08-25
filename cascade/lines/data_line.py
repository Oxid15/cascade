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
import socket
from collections import defaultdict
from getpass import getuser
from hashlib import md5
from typing import Any, Optional, Tuple, Type, Union

import pendulum
from typing_extensions import Literal

from ..base import Meta, MetaHandler
from ..base.serialization import ObjectHandler
from ..base.utils import (Version, get_latest_commit_hash, get_python_version,
                          get_uncommitted_changes, skeleton)
from ..data.dataset import Dataset
from .disk_line import DiskLine


class DataLine(DiskLine):
    def __init__(
        self,
        root: str,
        ds_cls: Type[Any] = Dataset,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        obj_backend: Literal["pickle"] = "pickle",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._hashes = defaultdict(lambda: defaultdict(dict))
        super().__init__(root, item_cls=ds_cls, meta_fmt=meta_fmt, *args, **kwargs)

        self._obj_handler = ObjectHandler(obj_backend)
        for name in self._item_names:
            with open(os.path.join(self._root, name, "HASHES"), "r") as f:
                skel_hash, meta_hash = f.read().split("\n")
                self._hashes[skel_hash][meta_hash] = Version(name)

    def _get_hashes(self, meta: Meta) -> Tuple[str, str]:
        skel = skeleton(meta)

        skel_str = str(skel)
        meta_str = str(meta)

        skel_hash = md5(str.encode(skel_str, "utf-8")).hexdigest()
        meta_hash = md5(str.encode(meta_str, "utf-8")).hexdigest()
        return skel_hash, meta_hash

    def get_latest_version(self) -> Optional[Version]:
        """
        Returns latest known version of a dataset or None
        if empty.
        """
        if len(self._hashes) > 0:
            max_version = Version("0.1")
            for sh in self._hashes:
                for mh in self._hashes[sh]:
                    if self._hashes[sh][mh] > max_version:
                        max_version = self._hashes[sh][mh]
            return max_version
        return None

    def get_version(self, ds: Dataset) -> Version:
        """
        Given a dataset, returns its version. If
        the dataset was seen previously, will retrieve the
        version and if not, will assign appropriate latest
        version.

        Does not record the info about dataset - use save()
        for that purposes.
        """
        meta = ds.get_meta()
        skel_hash, meta_hash = self._get_hashes(meta)
        return self._get_version(skel_hash, meta_hash)

    def _get_version(self, skel_hash: str, meta_hash: str) -> Version:
        if skel_hash in self._hashes:
            if meta_hash in self._hashes[skel_hash]:
                version = self._hashes[skel_hash][meta_hash]
            else:
                max_version = max(list(self._hashes[skel_hash].values()))
                version = max_version.bump_minor()
        else:
            if len(self._hashes):
                max_version = self.get_latest_version()
                version = max_version.bump_major()
            else:
                version = Version("0.1")

        return version

    def load(self, num: Union[int, str]) -> Dataset:
        """
        Loads a dataset by using its number or version string
        """
        if isinstance(num, int):
            path = os.path.join(self._root, self._item_names[num])
        elif isinstance(num, str):
            path = os.path.join(self._root, num)
        else:
            raise TypeError(
                f"Only accept the number of dataset or its version as input, got {type(num)}"
            )
        return self._obj_handler.load(path)

    def save(self, ds: Dataset, only_meta: bool = False) -> None:
        """
        Saves a dataset into a folder corresponding with its version.
        Version is determined by meta from get_meta method and consists of two parts.
        Major and minor like 0.1 or 2.12 etc. If the
        structure of the pipeline changed e.g. some new step added,
        then major version updates. An when the structure is the same, but meta changed
        in some way, then minor version is updated.
        """
        meta = ds.get_meta()
        obj_type = meta[0].get("type")
        if obj_type != "dataset":
            raise ValueError(
                f"Can only save meta of type `dataset` into a DataLine, got {obj_type}"
            )

        skel_hash, meta_hash = self._get_hashes(meta)
        version = self._get_version(skel_hash, meta_hash)
        version_str = str(version)

        if skel_hash not in self._hashes or meta_hash not in self._hashes[skel_hash]:
            self._item_names.append(version_str)

        self._hashes[skel_hash][meta_hash] = version
        full_path = os.path.join(self._root, version_str)

        meta[0]["path"] = full_path
        meta[0]["saved_at"] = pendulum.now(tz="UTC")
        meta[0]["version"] = version_str
        meta[0]["python_version"] = get_python_version()
        meta[0]["user"] = getuser()
        meta[0]["host"] = socket.gethostname()

        git_commit = get_latest_commit_hash()
        if git_commit:
            meta[0]["cwd"] = os.getcwd()
            meta[0]["git_commit"] = git_commit

        git_uncommitted = get_uncommitted_changes()
        if git_uncommitted is not None:
            meta[0]["git_uncommitted_changes"] = git_uncommitted

        os.makedirs(full_path, exist_ok=True)
        MetaHandler.write(os.path.join(full_path, "meta" + self._meta_fmt), meta)

        with open(os.path.join(self._root, version_str, "HASHES"), "w") as f:
            f.write("\n".join([skel_hash, meta_hash]))

        if not only_meta:
            self._obj_handler.save(ds, os.path.join(self._root, version_str))

        self.sync_meta()

    def __getitem__(self, num: int) -> Any:
        return self.load(num)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update({"type": "data_line"})
        meta[0]["latest_version"] = str(self.get_latest_version())
        return meta

    def _parse_item_name(self, item: Union[int, str]) -> str:
        if isinstance(item, str):
            name = Version(item)
            return str(name)
        else:
            return super()._parse_item_name(item)
