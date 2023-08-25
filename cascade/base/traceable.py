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


from dataclasses import dataclass, asdict
import os
import glob
import socket
import warnings
from typing import Dict, Union, Any, Literal, Iterable
import pendulum
from datetime import datetime

from . import PipeMeta, MetaFromFile, default_meta_format, supported_meta_formats


@dataclass
class Comment:
    id: str
    user: str
    host: str
    timestamp: datetime
    message: str


class Traceable:
    """
    Base class for everything that has metadata in Cascade
    Handles the logic of getting and updating internal meta prefix
    """

    def __init__(
        self,
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        description: Union[str, None] = None,
        tags: Union[Iterable[str], None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        meta_prefix: Union[Dict[Any, Any], str], optional
            The dictionary that is used to update object's meta in `get_meta` call.
            Due to the call of update can overwrite default values.
            If str - prefix assumed to be path and loaded using MetaHandler.
        description:
            String description of an object
        tags: Iterable[str], optional
            The list of tags to be added
        See also
        --------
        cascade.base.MetaHandler
        """
        if meta_prefix is None:
            meta_prefix = {}
        elif isinstance(meta_prefix, str):
            meta_prefix = self._read_meta_from_file(meta_prefix)
        self._meta_prefix = meta_prefix
        self.describe(description)

        if tags is not None:
            self.tags = set(tags)
        else:
            self.tags = set()

        self.comments = list()

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

        if hasattr(self, "description"):
            meta["description"] = self.description

        if hasattr(self, "tags"):
            meta["tags"] = list(self.tags)

        if hasattr(self, "comments"):
            comments = [asdict(comment) for comment in self.comments]
            meta["comments"] = comments

        return [meta]

    def update_meta(self, obj: Union[Dict[Any, Any], str]) -> None:
        """
        Updates `_meta_prefix`, which then updates
        dataset's meta when `get_meta()` is called
        """
        # TODO: fix this docstring
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

    def from_meta(self, meta: Dict[str, Any]) -> None:
        """
        Updates special fields from the given metadata

        Parameters
        ----------
        meta : Dict[str, Any]
        """
        if "description" in meta:
            self.describe(meta["description"])
        if "comments" in meta:
            for comment in meta["comments"]:
                self.comments.append(
                    Comment(**comment)
                )
        if "tags" in meta:
            self.tag(meta["tags"])

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

    def describe(self, desc: Union[str, None]):
        """
        Add description to an object

        Parameters
        ----------
        desc : Union[str, None]
            String description of an object.
            May be None to use the method in default initializer

        Raises
        ------
        TypeError
            If the input is not None and not a string either
        """
        if not isinstance(desc, str) and desc is not None:
            raise TypeError(f"Description should be str, got {type(desc)}")
        self.description = desc

    def tag(self, tag: Union[str, Iterable[str]]) -> None:
        """
        If tag is a string:
        Adds a tag to existing set
        Makes no duplicates since tags are set
        If tag is an iterable of strings:
        Adds a list of tags in one call
        Makes no duplicates since tags are set

        Parameters
        ----------
        tag : str
            A tag to add
        """
        if isinstance(tag, str):
            self.tags.add(tag)
        else:
            self.tags = self.tags.union(tag)

    def remove_tag(self, tag: Union[str, Iterable[str]]) -> None:
        """
        Removes a tag from the existing set
        if tag is a string, else
        removes a list of tags in one call

        Parameters
        ----------
        tag : str
            A tag to remove
        """
        if isinstance(tag, str):
            self.tags.remove(tag)
        else:
            self.tags = self.tags.difference(tag)

    def _find_latest_comment_id(self) -> str:
        if len(self.comments) == 0:
            return "0"
        return self.comments[-1].id

    def comment(self, message: str) -> None:
        comment_id = str(int(self._find_latest_comment_id()) + 1)
        comment = Comment(
            comment_id,
            os.getlogin(),
            socket.gethostname(),
            pendulum.now(),
            message
        )

        self.comments.append(comment)

    def remove_comment(self, id: int) -> None:
        for i, comment in enumerate(self.comments):
            if comment.id == id:
                self.comments.pop(i)
                return
        raise ValueError(f"Comment with {id} was not found")


class TraceableOnDisk(Traceable):
    """
    Common interface for Traceables that have
    their meta-data written on disk
    """
    def __init__(
        self,
        root: str,
        meta_fmt: Literal[".json", ".yml", ".yaml", None],
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)
        self._root = root

        ext = self._determine_meta_fmt()

        if ext is None and meta_fmt is None:
            self._meta_fmt = default_meta_format
        elif not ext:
            # Here we write meta first time and
            # don't know the real ext from file
            if meta_fmt not in supported_meta_formats:
                raise ValueError(f"Only {supported_meta_formats} are supported formats")
            self._meta_fmt = meta_fmt
        else:
            # Here we know the real extension and will
            # strictly use it regardless of what was passed
            self._meta_fmt = ext
            if meta_fmt != ext and meta_fmt is not None:
                warnings.warn(
                    f"Trying to set {meta_fmt} to the object that already has {ext} "
                    "on path {self._root}"
                )

    def _determine_meta_fmt(self) -> Union[str, None]:
        meta_paths = glob.glob(os.path.join(self._root, "meta.*"))
        if len(meta_paths) == 1:
            _, ext = os.path.splitext(meta_paths[0])
            return ext
        else:
            warnings.warn(
                f"Multiple meta files found in {self._root}"
            )

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
