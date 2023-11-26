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
from getpass import getuser
import os
import glob
import socket
import warnings
from typing import Dict, Union, Any, Literal, Iterable
import pendulum
from datetime import datetime

from . import PipeMeta, Meta, default_meta_format, supported_meta_formats, MetaIOError


@dataclass
class Comment:
    id: str
    user: str
    host: str
    timestamp: datetime
    message: str


@dataclass
class Link:
    id: str
    name: Union[str, None]
    uri: Union[str, None]
    meta: Union[PipeMeta, None]
    created_at: datetime

    def __post_init__(self) -> None:
        if self.uri is not None and os.path.exists(self.uri):
            self.uri = os.path.abspath(self.uri)


class Traceable:
    """
    Base class for everything that has metadata in Cascade
    Handles the logic of getting and updating internal meta prefix
    """

    def __init__(
        self,
        *args: Any,
        description: Union[str, None] = None,
        tags: Union[Iterable[str], None] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        description:
            String description of an object
        tags: Iterable[str], optional
            The list of tags to be added
        See also
        --------
        cascade.base.MetaHandler
        """
        self._meta_prefix = {}
        self.describe(description)

        if tags is not None:
            self.tags = set(tags)
        else:
            self.tags = set()

        self.comments = list()
        self.links = list()

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

        if hasattr(self, "links"):
            links = [asdict(link) for link in self.links]
            meta["links"] = links

        return [meta]

    def update_meta(self, meta: Union[PipeMeta, Meta]) -> None:
        """
        Updates `_meta_prefix`, which then updates
        dataset's meta when `get_meta()` is called

        Parameters
        ----------
        meta : Union[PipeMeta, Meta]
            The object to update with

        Raises
        ------
        ValueError
            If the list passed and it is not of the unit length
        """
        if not hasattr(self, "_meta_prefix"):
            self._warn_no_prefix()
            self._meta_prefix = {}

        if isinstance(meta, list):
            if len(meta) != 1:
                raise ValueError(
                    f"Object that was passed or read from path is a list of length {len(meta)}"
                    f"There is no clear way to update this object's meta"
                    f"using this kind of list"
                )
            self._meta_prefix.update(meta[0])
        else:
            self._meta_prefix.update(meta)

    @staticmethod
    def _warn_no_prefix() -> None:
        warnings.warn(
            "Object doesn't have _meta_prefix. "
            "This may mean super().__init__() wasn't"
            "called somewhere"
        )

    def from_meta(self, meta: Union[PipeMeta, Meta]) -> None:
        """
        Updates special fields from the given metadata

        Parameters
        ----------
        meta : Union[PipeMeta, Meta]
        """
        self.update_meta(meta)

        if not isinstance(meta, list):
            meta = [meta]

        if "description" in meta[0]:
            self.describe(meta[0]["description"])
        if "comments" in meta[0]:
            for comment in meta[0]["comments"]:
                self.comments.append(
                    Comment(**comment)
                )
        if "tags" in meta[0]:
            self.tag(meta[0]["tags"])

        if "links" in meta[0]:
            for link in meta[0]["links"]:
                self.links.append(
                    Link(**link)
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
            getuser(),
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

    def _find_latest_link_id(self) -> str:
        if len(self.links) == 0:
            return "0"
        return self.links[-1].id

    def link(self,
             obj: Union["Traceable", None] = None,
             name: Union[str, None] = None,
             uri: Union[str, None] = None,
             meta: Union[PipeMeta, None] = None,
             include: bool = True) -> None:
        """
        Links another object to this object. Links can contain
        name, URI and meta of the object.

        To create the link the Traceable can be passed - if include
        is True (by default) object's meta and string representation will be taken and saved with
        the link.

        If include is False get_meta will still be called, but only small set of
        specific fields will be taken.

        Link can be initialized without meta for example with only name
        or only URI. If path exists locally then it is automatically will
        be made absolute.

        If name or meta passed with the object at the same time
        they will override values from the object.

        The get_meta() of an object is resolved in the link method to
        prevent circular calls and other problems.

        Parameters
        ----------
        obj : Union[Traceable, None]
            The object to link
        name : Union[str, None], optional
            Name of the object, overrides obj name if passed, by default None
        uri : Union[str, None], optional
            URI of the object, by default None
        meta : Union[PipeMeta, None], optional
            Meta of the object, overrides obj meta if passed, by default None
        include : bool, optional
            Whether to include full meta of the object, by default True
        """
        if isinstance(obj, Traceable):
            if name is None:
                name = str(obj)
            if meta is None:
                if include:
                    meta = obj.get_meta()
                else:
                    obj_meta = obj.get_meta()
                    meta = [{
                        "type": obj_meta[0].get("type"),
                        "description": obj_meta[0].get("description"),
                        "tags": obj_meta[0].get("tags"),
                        "comments": obj_meta[0].get("comments"),
                    }]

        link_id = str(int(self._find_latest_link_id()) + 1)
        self.links.append(
            Link(link_id, name, uri, meta, pendulum.now(tz="UTC"))
        )

    def remove_link(self, id: str) -> None:
        """
        Removes a link given an index

        Parameters
        ----------
        idx : int
            Link's index
        """
        for i, link in enumerate(self.links):
            if link.id == id:
                self.links.pop(i)
                return
        raise ValueError(f"Link with {id} was not found")


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
        # TODO: maybe meta.* should become a global setting
        meta_paths = glob.glob(os.path.join(self._root, "meta.*"))
        if len(meta_paths) == 0:
            return
        elif len(meta_paths) == 1:
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
        except MetaIOError as e:
            warnings.warn(f"File writing error ignored: {e}")

    def _update_meta(self) -> None:
        """
        Reads meta if exists and updates it with new values
        writes back to disk

        If meta file exists and is only one, then reads it
        and writes back in the same format
        """

        meta = {}
        from . import MetaHandler

        try:
            meta = MetaHandler.read_dir(self._root)[0]
        except MetaIOError as e:
            warnings.warn(f"File reading error ignored: {e}")

        meta.update(self.get_meta()[0])

        try:
            MetaHandler.write_dir(self._root, [meta])
        except MetaIOError as e:
            warnings.warn(f"File writing error ignored: {e}")

    def get_root(self) -> str:
        return self._root

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["updated_at"] = pendulum.now(tz="UTC")
        return meta
