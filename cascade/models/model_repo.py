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
import warnings
import itertools
from typing import List, Iterable, Union, Any, Literal, Type, Generator
import shutil

import pendulum
from deepdiff.diff import DeepDiff

from ..base import (Traceable, MetaHandler, HistoryLogger,
                    JSONEncoder, supported_meta_formats, PipeMeta)
from .model import Model
from .model_line import ModelLine


class Repo(Traceable):
    """
    Base interface for repos of models.

    See also
    --------
    cascade.models.ModelRepo
    """
    root = None

    def reload(self) -> None:
        raise NotImplementedError()

    def __getitem__(self, key: str) -> ModelLine:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()


class ModelRepo(Repo):
    """
    An interface to manage experiments with several lines of models.
    When created, initializes an empty folder constituting a repository of model lines.

    Stores its meta-data in its root folder. With every run if the repo was already
    created earlier, updates its meta and logs changes in human-readable format in file history.log

    Example
    -------
    >>> from cascade.models import ModelRepo
    >>> from cascade.utils.baselines import ConstantBaseline
    >>> repo = ModelRepo('repo', meta_prefix={'description': 'This is a repo with one line for the example.'})
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
        lines: Union[Iterable[ModelLine], None] = None,
        overwrite: bool = False,
        meta_fmt: Literal['.json', '.yml', '.yaml'] = '.json',
        model_cls: Type = Model,
        log_history: bool = True,
        **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        folder:
            Path to a folder where ModelRepo needs to be created or already was created
            if folder does not exist, creates it
        lines: List[Dict]
            A list with parameters of model lines to add at creation or to initialize (alias for `add_model`)
        overwrite: bool
            if True will remove folder that is passed in first argument and start a new repo
            in that place
        meta_fmt: Literal['.json', '.yml', '.yaml']
            extension of repo's metadata files and that will be assigned to the lines by default
            `.json` and `.yml` or `.yaml` are supported
        model_cls:
            Default class for any ModelLine in repo
        See also
        --------
        cascade.models.ModelLine
        """
        super().__init__(**kwargs)
        self._model_cls = model_cls
        self._root = folder
        self._lines = dict()
        self._log_history = log_history

        assert meta_fmt in supported_meta_formats, \
            f'Only {supported_meta_formats} are supported formats'
        self._meta_fmt = meta_fmt
        if overwrite and os.path.exists(self._root):
            shutil.rmtree(self._root)

        os.makedirs(self._root, exist_ok=True)

        self._mh = MetaHandler()
        if self._log_history:
            self._hl = HistoryLogger(os.path.join(self._root, 'history.yml'))
        self._load_lines()

        if lines is not None:
            for line in lines:
                self.add_line(**line)

        self._update_meta()

    def _load_lines(self) -> None:
        self._lines = {
            name: ModelLine(os.path.join(self._root, name),
                            model_cls=self._model_cls,
                            meta_prefix=self._meta_prefix,
                            meta_fmt=self._meta_fmt)
            for name in sorted(os.listdir(self._root))
            if os.path.isdir(os.path.join(self._root, name))}

    def add_line(
            self,
            name: Union[str, None] = None,
            *args: Any,
            meta_fmt: Union[str, None] = None,
            **kwargs: Any
    ) -> ModelLine:
        """
        Adds new line to repo if it doesn't exist and returns it.
        If line exists, defines it in repo with parameters provided.

        Supports all the parameters of ModelLine using args and kwargs.

        Parameters:
            name: str, optional
                Name of the line. It is used to name a folder of line.
                Repo prepends it with `self._root` before creating.
                Optional argument. If omitted - names new line automatically
                using f'{len(self):0>5d}'
            meta_fmt: str, optional
                Format of meta files. Supported values are the same as for repo.
                If omitted, inherits format from repo.
        See also
        --------
            cascade.models.ModelLine
       """
        # TODO: use default model_cls
        if name is None:
            name = f'{len(self):0>5d}'
            if name in self.get_line_names():
                # Name can appear in the repo if the user manually
                # removed the lines from the middle of the repo

                # This will be handled strictly
                # until it will become clear that some solution needed
                raise RuntimeError(f'Line {name} already exists in {self}')

        folder = os.path.join(self._root, name)
        if meta_fmt is None:
            meta_fmt = self._meta_fmt
        line = ModelLine(folder,
                         *args,
                         meta_prefix=self._meta_prefix,
                         meta_fmt=meta_fmt,
                         **kwargs)
        self._lines[name] = line

        self._update_meta()
        return line

    def __getitem__(self, key: Union[str, int]) -> ModelLine:
        """
        Returns
        -------
        line: ModelLine
           existing line of the name passed in `key`
        """
        if isinstance(key, str):
            return self._lines[key]
        elif isinstance(key, int):
            return self._lines[list(self._lines.keys())[key]]
        else:
            raise TypeError(f'{type(key)} is not supported as key')

    def __iter__(self) -> Generator[ModelLine, None, None]:
        for line in self._lines:
            yield self.__getitem__(line)

    def __len__(self) -> int:
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self._lines)

    def __repr__(self) -> str:
        return f'ModelRepo in {self._root} of {len(self)} lines'

    def _update_meta(self) -> None:
        # Reads meta if exists and updates it with new values
        # writes back to disk
        meta_path = os.path.join(self._root, 'meta' + self._meta_fmt)

        meta = {}
        if os.path.exists(meta_path):
            try:
                meta = self._mh.read(meta_path)[0]
            except IOError as e:
                warnings.warn(f'File reading error ignored: {e}')

        if self._log_history:
            self_meta = JSONEncoder().obj_to_dict(self.get_meta()[0])
            diff = DeepDiff(meta, self_meta, exclude_paths=["root['name']", "root['updated_at']"])
            if len(diff) != 0:
                self._hl.log(self_meta)

        meta.update(self.get_meta()[0])
        try:
            self._mh.write(meta_path, [meta])
        except IOError as e:
            warnings.warn(f'File writing error ignored: {e}')

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({
            'root': self._root,
            'len': len(self),
            'updated_at': pendulum.now(tz='UTC'),
            'type': 'repo'
        })
        return meta

    def reload(self) -> None:
        """
        Updates internal state.
        """
        self._load_lines()
        self._update_meta()

    def __add__(self, repo):
        return ModelRepoConcatenator([self, repo])

    def get_line_names(self) -> List[str]:
        """
        Returns list of line names.
        """
        return list(self._lines.keys())


class ModelRepoConcatenator(Repo):
    """
    The class to concatenate different Repos.
    For the ease of use please, don't use it directly.
    Just do `repo = repo_1 + repo_2` to unify two or more repos.
    """
    def __init__(self, repos: Iterable[Repo], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._repos = repos

    def __getitem__(self, key) -> ModelLine:
        pair = key.split('_')
        if len(pair) <= 2:
            raise KeyError(f'Key {key} is not in required format \
            `<repo_idx>_..._<line_name>`. \
            Please, use the key in this format. For example `0_line_1`')
        idx, line_name = pair[0], '_'.join(pair[1:])
        idx = int(idx)

        return self._repos[idx][line_name]

    def __len__(self) -> int:
        return sum([len(repo) for repo in self._repos])

    def __iter__(self) -> Generator[ModelLine, None, None]:
        # this flattens the list of lines
        for line in itertools.chain(*[[line for line in repo] for repo in self._repos]):
            yield line

    def __add__(self, repo: ModelRepo):
        return ModelRepoConcatenator([self, repo])

    def __repr__(self) -> str:
        return f'ModelRepoConcatenator of {len(self._repos)} repos, {len(self)} lines total'

    def reload(self) -> None:
        for repo in self._repos:
            repo.reload()
