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
from hashlib import md5
from typing import Any, Tuple

import pendulum
from typing_extensions import deprecated

from ..base import Meta, MetaHandler, supported_meta_formats
from ..base.utils import skeleton
from .dataset import BaseDataset, T
from .modifier import Modifier


@deprecated("Deprecated since 0.14.0. Consider using cascade.lines.DataLine"
            " with line.save(ds, only_meta=True) if you do not want"
            " to save pipeline objects, but only to track versions")
class VersionAssigner(Modifier):
    """
    Class for automatic data versioning using metadata.
    ``VersionAssigner`` is a simple ``Modifier`` that tracks changes in metadata and assigns
    dataset a version considering changes in meta.
    The version consists of two parts, namely major and minor in the format ``MAJOR.MINOR`` just
    like in semantic versioning. The meaning of parts is the following: *major* number changes
    if there are changes in the structure of the pipeline e.g. some dataset was added/removed;
    *minor* number changes in case of any metadata change e.g. new data arrived and changed
    the length of modifiers on pipeline.

    Example
    -------
    >>> # Set up the pipeline
    >>> from cascade import data as cdd
    >>> ds = cdd.Wrapper([0, 1, 2, 3, 4])
    >>> ds = VersionAssigner(ds, 'data_log.yml') # can be any supported meta format
    >>> print(ds.version)
        0.0

    >>> # Changes its structure - add new modifier
    >>> ds = cdd.Wrapper([0, 1, 2, 3, 4])
    >>> ds = cdd.RangeSampler(ds, 0, len(ds), 2)
    >>> ds = VersionAssigner(ds, 'data_log.yml')
    >>> print(ds.version)
        1.0

    >>> # Revert changes - version downgrades back
    >>> ds = cdd.Wrapper([0, 1, 2, 3, 4])
    >>> ds = VersionAssigner(ds, 'data_log.yml')
    >>> print(ds.version)
        0.0

    >>> # Update input data - minor update
    >>> ds = cdd.Wrapper([0, 1, 2, 3, 4, 5])
    >>> ds = VersionAssigner(ds, 'data_log.yml')
    >>> print(ds.version)
        0.1

    Note
    ----
    Some limitations are present. If meta data of some dataset has
    something random or run-dependent like for example memory
    address of an object or time of creation, then the version will
    bump on every run.
    """

    def __init__(
        self,
        dataset: BaseDataset[T],
        path: str,
        verbose: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
            dataset: Dataset
                a dataset to infer version to
            path: str
                a path to a version log file of this dataset can be of any supported
                meta format
        """
        super().__init__(dataset, *args, **kwargs)
        self._assign_path(path)
        self._versions = {"versions": {}, "type": "version_history"}

        # get meta for info about pipeline
        meta = self._dataset.get_meta()
        pipeline = skeleton(meta)

        meta_str = str(meta)
        pipeline_str = str(pipeline)

        # identify pipeline
        meta_hash = md5(str.encode(meta_str, "utf-8")).hexdigest()
        pipe_hash = md5(str.encode(pipeline_str, "utf-8")).hexdigest()

        if os.path.exists(self._root):
            self._versions = MetaHandler.read(self._root)

            if pipe_hash in self._versions["versions"]:
                if meta_hash in self._versions["versions"][pipe_hash]:
                    self.version = self._versions["versions"][pipe_hash][meta_hash][
                        "version"
                    ]
                else:
                    last_ver = self._get_last_version_from_pipe(pipe_hash)
                    major, minor = self._split_ver(last_ver)
                    minor += 1
                    self.version = self._join_ver(major, minor)
                    self._versions["versions"][pipe_hash][meta_hash] = {
                        "version": self.version,
                        "meta": meta,
                        "pipeline": pipeline,
                        "updated_at": str(pendulum.now(tz="UTC")),
                    }
            else:
                last_ver = self._get_last_version()
                major, minor = self._split_ver(last_ver)
                major += 1
                self.version = self._join_ver(major, minor)
                self._versions["versions"][pipe_hash] = {}
                self._versions["versions"][pipe_hash][meta_hash] = {
                    "version": self.version,
                    "meta": meta,
                    "pipeline": pipeline,
                    "updated_at": str(pendulum.now(tz="UTC")),
                }

            MetaHandler.write(self._root, self._versions)
        else:
            self.version = "0.0"
            self._versions["versions"][pipe_hash] = {}
            self._versions["versions"][pipe_hash][meta_hash] = {
                "version": self.version,
                "meta": meta,
                "pipeline": pipeline,
                "updated_at": str(pendulum.now(tz="UTC")),
            }
            MetaHandler.write(self._root, self._versions)

        if verbose:
            print("Dataset version:", self.version)

    def _assign_path(self, path: str) -> None:
        _, ext = os.path.splitext(path)
        if ext == "":
            raise ValueError(f"Provided path {path} has no extension")

        assert (
            ext in supported_meta_formats
        ), f"Only {supported_meta_formats} are supported formats"
        self._root = path

    def _split_ver(self, ver: str) -> Tuple[int, int]:
        major, minor = ver.split(".")
        return int(major), int(minor)

    def _join_ver(self, major: int, minor: int) -> str:
        return f"{major}.{minor}"

    def _get_last_version_from_pipe(self, pipe_hash: str) -> str:
        versions = [
            item["version"] for item in self._versions["versions"][pipe_hash].values()
        ]
        versions = sorted(versions)
        return versions[-1]

    def _get_last_version(self) -> str:
        versions_flat = []
        for pipe_hash in self._versions["versions"]:
            versions_flat += [
                item["version"]
                for item in self._versions["versions"][pipe_hash].values()
            ]
        versions = sorted(versions_flat)
        return versions[-1]

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["version"] = self.version
        return meta


@deprecated("Deprecated since 0.14.0 consider using"
            " cascade.lines.DataLine.get_version method instead")
def version(ds: BaseDataset[T], path: str) -> str:
    """
    Returns version of a dataset using VersionAssigner

    Parameters
    ----------
    ds : Dataset[T]
        Dataset to track and version
    path : str
        Path to the version log of a dataset, will be created if does
        not exists

    Returns
    -------
    str
        Version in two parts like 2.1 or 0.1

    See also
    --------
    cascade.data.VersionAssigner
    """
    ds = VersionAssigner(ds, path)
    return ds.version
