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

import itertools
import os
import shutil
from typing import Any, Dict, Iterable, Iterator, List, Type, Union

from typing_extensions import Literal, deprecated

from ..base import Meta, Traceable, TraceableOnDisk
from ..data import T
from ..version import __version__
from .model import Model
from .model_line import ModelLine


class Repo(Traceable):
    """
    Base interface for repos of models. Repo is the collection of Lines.

    See also
    --------
    cascade.models.ModelRepo
    """

    def __init__(
        self,
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)
        self._lines = dict()

    def __getitem__(self, key: str) -> ModelLine:
        raise NotImplementedError()

    def __len__(self) -> int:
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self._lines)

    def __iter__(self) -> Iterator[T]:
        for line in self._lines:
            yield self.__getitem__(line)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root,
                "len": len(self),
                "type": "repo",
                "cascade_version": __version__,
            }
        )
        return meta

    def get_line_names(self) -> List[str]:
        """
        Returns list of line names.
        """
        return list(self._lines.keys())

    def reload(self) -> None:
        pass


@deprecated(
    "cascade.models.SingleLineRepo is deprecated, consider using"
    " cascade.repos.SingleLineRepo instead"
)
class SingleLineRepo(Repo):
    def __init__(
        self,
        line: ModelLine,
        *args: Any,
        meta_prefix: Union[Dict[Any, Any], str, None] = None,
        **kwargs: Any,
    ) -> None:
        self._root = line.get_root()
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)
        self._lines = {line.get_root(): {"args": [], "kwargs": dict()}}
        self._line = line

    def __getitem__(self, key: str) -> ModelLine:
        if key in self._lines:
            return self._line
        else:
            raise KeyError(
                f"The only line is {list(self._lines.keys())[0]}, {key} does not exist"
            )

    def __repr__(self) -> str:
        return f"SingleLine in {self._root}"

    def get_root(self):
        return self._root

    def reload(self) -> None:
        self._line.reload()


@deprecated(
    "cascade.models.ModelRepo is deprecated, consider using cascade.repos.Repo instead"
)
class ModelRepo(Repo, TraceableOnDisk):
    """
    An interface to manage experiments with several lines of models.
    When created, initializes an empty folder constituting a repository of model lines.

    Stores its metadata in its root folder. With every run if the repo was already
    created earlier, updates its meta and logs changes in human-readable format in
    history file

    Example
    -------
    >>> from cascade.models import ModelRepo
    >>> from cascade.utils.baselines import ConstantBaseline
    >>> repo = ModelRepo('repo', meta_prefix={'description': 'This is a repo with one line.'})
    >>> line = repo.add_line('model', ConstantBaseline)
    >>> model = ConstantBaseline(1)
    >>> model.fit()
    >>> line.save(model)


    >>> from cascade.models import ModelRepo
    >>> from cascade.utils.baselines import ConstantBaseline
    >>> repo = ModelRepo('repo', lines=[dict(name='constant', model_cls=ConstantBaseline)])
    >>> model = ConstantBaseline()
    >>> model.fit()
    >>> repo['constant'].save(model)
    """

    def __init__(
        self,
        folder: str,
        *args: Any,
        lines: Union[Iterable[ModelLine], None] = None,
        overwrite: bool = False,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        model_cls: Union[Type, Dict[str, Type]] = Model,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        folder:
            Path to a folder where ModelRepo needs to be created or already was created
            if folder does not exist, creates it
        lines: List[Dict]
            A list with parameters of model lines to add at creation or to
            initialize (alias for ``add_model``)
        overwrite: bool
            if True will remove folder that is passed in first argument and start a new repo
            in that place
        meta_fmt: Literal['.json', '.yml', '.yaml']
            extension of repo's metadata files and that will be assigned to the lines by default
            ``.json`` and ``.yml`` or ``.yaml`` are supported
        model_cls:
            Default class for any ModelLine in repo
        See also
        --------
        cascade.models.ModelLine
        """

        super().__init__(folder, meta_fmt, *args, **kwargs)
        self._model_cls = model_cls

        if overwrite and os.path.exists(self._root):
            shutil.rmtree(self._root)

        os.makedirs(self._root, exist_ok=True)
        self._lines = {
            name: {"args": [], "kwargs": dict()}
            for name in sorted(os.listdir(self._root))
            if os.path.isdir(os.path.join(self._root, name))
        }

        if lines is not None:
            for line in lines:
                name = line["name"]
                del line["name"]

                self._lines[name] = {"args": [], "kwargs": line}

        self.sync_meta()

    def add_line(
        self,
        name: Union[str, None] = None,
        *args: Any,
        meta_fmt: Union[str, None] = None,
        **kwargs: Any,
    ) -> ModelLine:
        """
        Adds new line to repo if it doesn't exist and returns it.
        If line exists, defines it in repo with parameters provided.

        Supports all the parameters of ModelLine using args and kwargs.

        Parameters:
            name: str, optional
                Name of the line. It is used to name a folder of line.
                Repo prepends it with ``self._root`` before creating.
                Optional argument. If omitted - names new line automatically
                using ``f'{len(self):0>5d}'``
            meta_fmt: str, optional
                Format of meta files. Supported values are the same as for repo.
                If omitted, inherits format from repo.
        See also
        --------
            cascade.models.ModelLine
        """
        # TODO: use default model_cls
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

        line = ModelLine(folder, *args, meta_fmt=meta_fmt, **kwargs)
        return line

    def __getitem__(self, key: Union[str, int]) -> ModelLine:
        """
        Returns
        -------
        line: ModelLine
           existing line of the name passed in ``key``
        """
        if isinstance(key, int):
            key = list(self._lines.keys())[key]
        elif not isinstance(key, str):
            raise TypeError(f"{type(key)} is not supported as key")

        if key in self._lines:
            return ModelLine(
                os.path.join(self._root, key),
                *self._lines[key]["args"],
                **self._lines[key]["kwargs"],
            )
        else:
            raise KeyError(f"Line {key} does not exist in {self}")

    def __repr__(self) -> str:
        return f"ModelRepo in {self._root} of {len(self)} lines"

    def reload(self) -> None:
        """
        Updates internal state
        """
        super().reload()
        self._update_lines()
        self.sync_meta()

    def __add__(self, repo: "ModelRepo") -> "ModelRepoConcatenator":
        return ModelRepoConcatenator([self, repo])

    def load_model_meta(self, model: str) -> Meta:
        """
        Loads metadata of a model from disk

        Parameters
        ----------
        model : str
            model slug e.g. ``fair_squid_of_bliss``

        Returns
        -------
        Meta
            Model metadata

        Raises
        ------
        FileNotFoundError
            Raises if failed to find the model with slug specified
        """

        for name in self._lines:
            try:
                line = ModelLine(
                    os.path.join(self._root, name),
                    *self._lines[name]["args"],
                    **self._lines[name]["kwargs"],
                )
                meta = line.load_model_meta(model)
            except FileNotFoundError:
                continue
            else:
                return meta
        raise FileNotFoundError(
            f"Failed to find the model {model} in the repo at {self._root}"
        )

    def _update_lines(self) -> None:
        for name in sorted(os.listdir(self._root)):
            if (
                os.path.isdir(os.path.join(self._root, name))
                and name not in self._lines  # noqa: W503
            ):
                self._lines[name] = {"args": [], "kwargs": dict()}


@deprecated(
    "Concatenating Repos is deprecated since"
    " 0.14.0 and will be removed by 0.15.0"
    " Use Workspaces instead",
    category=DeprecationWarning,
    stacklevel=1,
)
class ModelRepoConcatenator(Repo):
    """
    Deprecated

    The class to concatenate different Repos.
    For the ease of use please, don't use it directly.
    Just do ``repo = repo_1 + repo_2`` to unify two or more repos.
    """

    def __init__(self, repos: Iterable[Repo], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._repos = repos

    def __getitem__(self, key) -> ModelLine:
        pair = key.split("_")
        if len(pair) <= 2:
            raise KeyError(
                f"Key {key} is not in required format \
            ``<repo_idx>_..._<line_name>``. \
            Please, use the key in this format. For example ``0_line_1``"
            )
        idx, line_name = pair[0], "_".join(pair[1:])
        idx = int(idx)

        return self._repos[idx][line_name]

    def __len__(self) -> int:
        return sum([len(repo) for repo in self._repos])

    def __iter__(self) -> Iterator[T]:
        # this flattens the list of lines
        for line in itertools.chain(*[[line for line in repo] for repo in self._repos]):
            yield line

    def __add__(self, repo: ModelRepo):
        return ModelRepoConcatenator([self, repo])

    def __repr__(self) -> str:
        return f"ModelRepoConcatenator of {len(self._repos)} repos, {len(self)} lines total"

    def reload(self) -> None:
        for repo in self._repos:
            repo.reload()
