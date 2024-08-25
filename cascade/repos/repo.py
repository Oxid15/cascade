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
import shutil
from typing import Any, List, Optional, Union

from typing_extensions import Literal

from ..base import Meta, TraceableOnDisk, ZeroMetaError
from ..lines import Line
from .base_repo import BaseRepo
from .line_factory import LineFactory


class Repo(BaseRepo, TraceableOnDisk):
    """
    An interface to manage series of experiments called lines.
    When created, initializes an empty folder constituting a repository of lines.

    Example
    -------
    >>> from cascade.base import Repo
    >>> from cascade.utils.baselines import ConstantBaseline
    >>> repo = Repo("repo")
    >>> repo.describe("This is a repo with one line for the example.")
    >>> line = repo.add_line("const", model_cls=ConstantBaseline)
    >>> model = line.add_model()
    >>> model.fit()
    >>> line.save(model)
    """

    def __init__(
        self,
        folder: str,
        *args: Any,
        overwrite: bool = False,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        folder:
            Path to a folder where Repo needs to be created or already was created
            if folder does not exist, creates it
        overwrite: bool
            if True will remove folder that is passed in first argument and start a new repo
            in that place
        meta_fmt: Literal['.json', '.yml', '.yaml']
            extension of repo's metadata files and that will be assigned to the lines by default
            ``.json`` and ``.yml`` or ``.yaml`` are supported

        See also
        --------
        cascade.base.Line
        cascade.data.DataLine
        cascade.models.ModelLine
        """
        super().__init__(path=folder, root=folder, meta_fmt=meta_fmt, *args, **kwargs)

        if overwrite and os.path.exists(self._root):
            shutil.rmtree(self._root)

        os.makedirs(self._root, exist_ok=True)
        self._lines = {
            name: {"args": [], "kwargs": dict()}
            for name in sorted(os.listdir(self._root))
            if os.path.isdir(os.path.join(self._root, name))
        }

        if "lines" in kwargs:
            raise ValueError(
                "lines was removed in 0.14.0, consider using add_line method instead"
            )

        self.sync_meta()

    def add_line(
        self,
        name: Optional[str] = None,
        line_type: Literal["data", "model", None] = "model",
        *args: Any,
        meta_fmt: Literal[".json", ".yml", ".yaml", None] = None,
        **kwargs: Any,
    ) -> Line:
        """
        Adds new line to repo if it doesn't exist and returns it.
        If line exists, defines it in repo with parameters provided.

        Supports all the parameters of Line using args and kwargs.

        Parameters:
            name: str, optional

            meta_fmt: str, optional

        See also
        --------
            cascade.base.Line
        Parameters
        ----------
        name : Optional[str], optional
            Name of the line. It is used to name a folder of line.
            Repo prepends it with ``self._root`` before creating.
            Optional argument. If omitted - names new line automatically
            using f'{len(self):0>5d}', by default None
        line_type : Literal["data", "model"]], by default "model"
            The type of model line to create, by default None
        meta_fmt : Literal[".json", ".yml", ".yaml", None], by default None
            Format of meta files. Supported values are the same as for repo.
            If omitted, inherits format from repo., by default None

        Returns
        -------
        Line
            Created or recreated model line

        Raises
        ------
        RuntimeError
            If line with the computed name already exists
        TypeError
            _description_
        IOError
            _description_
        """
        if name is None:
            name = f"{len(self):0>5d}"
            if name in self.get_line_names():
                # Name can appear in the repo if the user manually
                # removed the lines from the middle of the repo

                # This will be handled strictly
                # until it will become clear that some solution needed
                raise RuntimeError(f"Line {name} already exists in {self}")

        folder = os.path.join(self._root, name)
        if meta_fmt is None:
            meta_fmt = self._meta_fmt

        self._lines[name] = {"args": args, "kwargs": {"meta_fmt": meta_fmt, **kwargs}}
        self.sync_meta()

        if line_type is None:
            try:
                line = LineFactory.read(folder)
            except TypeError as e:
                raise TypeError(
                    f"line_type was {line_type}, which is incompatible with line {name}"
                ) from e
            except ZeroMetaError as e:
                raise IOError(
                    f"Did not found meta in {folder}, pass `line_cls`"
                    " if you want to create a line"
                ) from e
        else:
            line = LineFactory.create(
                folder, line_type=line_type, *args, meta_fmt=meta_fmt, **kwargs
            )
        return line

    def __getitem__(self, key: Union[str, int]):
        """
        Returns
        -------
        line: Line
           existing line of the name passed in ``key``
        """
        if isinstance(key, int):
            key = list(self._lines.keys())[key]
        elif not isinstance(key, str):
            raise TypeError(f"{type(key)} is not supported as key")

        if key in self._lines:
            return LineFactory.read(
                os.path.join(self._root, key),
                *self._lines[key]["args"],
                **self._lines[key]["kwargs"],
            )
        else:
            raise KeyError(f"Line {key} does not exist in {self}")

    def __repr__(self) -> str:
        return f"Repo in {self._root} of {len(self)} lines"

    def reload(self) -> None:
        """
        Updates internal state
        """
        self._update_lines()
        self.sync_meta()

    def load_obj_meta(self, obj: str) -> Meta:
        """
        Loads metadata of an object inside repo from disk

        Parameters
        ----------
        obj : str
            obj slug e.g. ``fair_squid_of_bliss``

        Returns
        -------
        Meta
            Obj metadata

        Raises
        ------
        FileNotFoundError
            Raises if failed to find the obj with slug specified
        """

        for name in self._lines:
            try:
                line = LineFactory.read(
                    os.path.join(self._root, name),
                    *self._lines[name]["args"],
                    **self._lines[name]["kwargs"],
                )
                meta = line.load_obj_meta(obj)
            except FileNotFoundError:
                continue
            else:
                return meta
        raise FileNotFoundError(
            f"Failed to find the object {obj} in the repo at {self._root}"
        )

    def _update_lines(self) -> None:
        for name in sorted(os.listdir(self._root)):
            if (
                os.path.isdir(os.path.join(self._root, name))
                and name not in self._lines  # noqa: W503
            ):
                self._lines[name] = {"args": [], "kwargs": dict()}

    def __len__(self) -> int:
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self._lines)

    def get_line_names(self) -> List[str]:
        """
        Returns list of line names.
        """
        return list(self._lines.keys())
