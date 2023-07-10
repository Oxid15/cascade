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


import os
import glob
import warnings
from typing import Dict, Union, Any, Literal
import pendulum

from cascade.base import PipeMeta
from . import PipeMeta, MetaFromFile, supported_meta_formats


class Traceable:
    """
    Base class for everything that has metadata in Cascade
    Handles the logic of getting and updating internal meta prefix
    """

    def __init__(
        self,
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        meta_prefix: Union[Dict[Any, Any], str], optional
            The dictionary that is used to update object's meta in `get_meta` call.
            Due to the call of update can overwrite default values.
            If str - prefix assumed to be path and loaded using MetaHandler.

        See also
        --------
        cascade.base.MetaHandler
        """
        if meta_prefix is None:
            meta_prefix = {}
        elif isinstance(meta_prefix, str):
            meta_prefix = self._read_meta_from_file(meta_prefix)
        self._meta_prefix = meta_prefix

    @staticmethod
    def _read_meta_from_file(path: str) -> MetaFromFile:
        from . import MetaHandler

        return MetaHandler.read(path)

    def get_meta(self) -> PipeMeta:
        """
        Returns
        -------
        meta: PipeMeta
            A list where first element is this object's metadata.
            All other elements represent the other stages of pipeline if present.

            Meta can be anything that is worth to document about
            the object and its properties.

            Meta is a list (see PipeMeta type alias) to allow the formation of pipelines.
        """
        meta = {"name": repr(self)}
        if hasattr(self, "_meta_prefix"):
            meta.update(self._meta_prefix)
        else:
            self._warn_no_prefix()
        return [meta]

    def update_meta(self, obj: Union[Dict[Any, Any], str]) -> None:
        """
        Updates `_meta_prefix`, which then updates
        dataset's meta when `get_meta()` is called
        """
        if isinstance(obj, str):
            obj = self._read_meta_from_file(obj)

        if isinstance(obj, list):
            raise RuntimeError(
                "Object that was passed or read from path is a list."
                "There is no clear way how to update this object's meta"
                "using list"
            )

        if hasattr(self, "_meta_prefix"):
            self._meta_prefix.update(obj)
        else:
            self._warn_no_prefix()

    @staticmethod
    def _warn_no_prefix() -> None:
        warnings.warn(
            "Object doesn't have _meta_prefix. "
            "This may mean super().__init__() wasn't"
            "called somewhere"
        )

    def __repr__(self) -> str:
        """
        Returns
        -------
        repr: str
            Representation of a Traceable. This repr used as a name for get_meta() method
            by default gives the name of class from basic repr

        See also
        --------
        cascade.data.Traceable.get_meta()
        """
        # Removes adress part of basic object repr and leading < symbol
        return super().__repr__().split()[0][1:]


class TraceableOnDisk(Traceable):
    """
    Common interface for Traceables that have
    their meta-data written on disk
    """
    def __init__(
        self,
        root: str,
        meta_fmt: Literal[".json", ".yml", ".yaml"],
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)
        self._root = root
        if meta_fmt not in supported_meta_formats:
            raise ValueError(f"Only {supported_meta_formats} are supported formats")
        self._meta_fmt = meta_fmt

    def _create_meta(self) -> None:
        meta_path = sorted(glob.glob(os.path.join(self._root, "meta.*")))
        # Object was created before -> update
        if len(meta_path) > 0:
            self._update_meta()
            return

        created = str(pendulum.now(tz="UTC"))
        meta = self.get_meta()
        meta[0].update({"created_at": created})

        from . import MetaHandler

        try:
            MetaHandler.write(os.path.join(self._root, "meta" + self._meta_fmt), meta)
        except IOError as e:
            warnings.warn(f"File writing error ignored: {e}")

    def _update_meta(self) -> None:
        """
        Reads meta if exists and updates it with new values
        writes back to disk

        If meta file exists and is only one, then reads it
        and writes back in the same format
        """

        meta_path = sorted(glob.glob(os.path.join(self._root, "meta.*")))

        if len(meta_path) == 0:
            return

        if len(meta_path) > 1:
            warnings.warn(
                f"There are {len(meta_path)} meta files in {self._root}, failed to update meta"
            )
            return

        meta = {}
        from . import MetaHandler

        meta_path = meta_path[0]
        try:
            meta = MetaHandler.read(meta_path)[0]
        except IOError as e:
            warnings.warn(f"File reading error ignored: {e}")

        meta.update(self.get_meta()[0])
        try:
            MetaHandler.write(meta_path, [meta])
        except IOError as e:
            warnings.warn(f"File writing error ignored: {e}")

    def get_root(self) -> str:
        return self._root

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["updated_at"] = pendulum.now(tz="UTC")
        return meta
