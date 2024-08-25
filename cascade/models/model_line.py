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
import traceback
from getpass import getuser
from typing import Any, Dict, List, Optional, Type, Union

import pendulum
from typing_extensions import Literal, deprecated

from ..base import Meta, MetaHandler, TraceableOnDisk
from ..base.utils import (
    generate_slug,
    get_latest_commit_hash,
    get_python_version,
    get_uncommitted_changes,
)
from ..version import __version__
from .model import Model


@deprecated(
    "cascade.models.ModelLine is deprecated, consider using cascade.lines.ModelLine instead"
)
class ModelLine(TraceableOnDisk):
    """
    A manager for a line of models. Used by Repo to access models on disk.
    A line of models is typically models with the same hyperparameters and architecture,
    but different epochs or trained using different data.
    """

    def __init__(
        self,
        folder: str,
        model_cls: Type[Any] = Model,
        meta_fmt: Literal[".json", ".yml", ".yaml", None] = None,
        **kwargs: Any,
    ) -> None:
        """
        All models in line should be instances of the same class.

        Parameters
        ----------
        folder: str
            Path to a folder where ModelLine will be created or already was created.
            If folder does not exist, creates it
        model_cls: type, optional
            A class of models in line. ModelLine uses this class to reconstruct a model
        meta_fmt: Literal[".json", ".yml", ".yaml", None], optional
            Format in which to store meta data.
        See also
        --------
        cascade.repos.Repo
        """

        super().__init__(folder, meta_fmt, **kwargs)
        self._model_cls = model_cls
        self._root = os.path.abspath(folder)
        self._model_names = []
        self._slug2name_cache = dict()
        if os.path.exists(self._root):
            self._load_model_names()
        else:
            # No folder -> create
            os.mkdir(self._root)

        self.sync_meta()

    def _load_model_names(self) -> None:
        if not os.path.isdir(self._root):
            raise ValueError(f"folder should be directory, got `{self._root}`")

        self._model_names = sorted(
            [
                model_folder
                for model_folder in os.listdir(self._root)
                if os.path.isdir(os.path.join(self._root, model_folder))
            ]
        )

    def reload(self) -> None:
        # Here update slugs
        self._load_model_names()

    def __getitem__(self, num: int) -> Model:
        """
        Loads the model using ``load`` method of a given class

        Returns
        -------
            model: Model
                a loaded model
        """
        model = self.load(num, only_meta=True)
        return model

    def __len__(self) -> int:
        """
        Returns
        -------
        A number of models in line
        """
        return len(self._model_names)

    def load(self, num: int, only_meta: bool = False) -> Model:
        """
        Loads a model

        Parameters
        ----------
        num : int
            Model number in line
        only_meta : bool, optional
            If True doesn't load model's artifacts, by default False
        """
        model = self._model_cls.load(os.path.join(self._root, self._model_names[num]))
        if not only_meta:
            model.load_artifact(
                os.path.join(self._root, self._model_names[num], "artifacts")
            )

        return model

    def _model_name_by_num(self, num: int):
        return f"{num:0>5d}"

    def _read_meta_by_name(self, name: str) -> Meta:
        meta = MetaHandler.read_dir(os.path.join(self._root, name))
        return meta

    def _find_name_by_slug(self, slug: str) -> Optional[str]:
        if slug in self._slug2name_cache:
            return self._slug2name_cache[slug]

        for name in self._model_names:
            filepath = os.path.join(self._root, name, "SLUG")
            if not os.path.exists(filepath):
                continue
            with open(filepath, "r") as f:
                slug_from_file = f.read()
                self._slug2name_cache[slug_from_file] = name
                if slug == slug_from_file:
                    return name

    def _parse_model_name(self, model: Union[str, int]) -> str:
        if isinstance(model, int):
            name = self._model_name_by_num(model)
        elif isinstance(model, str):
            name = self._find_name_by_slug(model)
        else:
            raise TypeError(f"The argument of type {type(model)} is not supported")

        if not name:
            raise FileNotFoundError(
                f"Failed to find the model {model} in the line at {self._root}"
            )
        return name

    def load_model_meta(self, model: Union[str, int]) -> Meta:
        """
        Loads metadata of a model from disk

        Parameters
        ----------
        model : Union[str, int]
            model slug e.g. ``fair_squid_of_bliss`` or number

        Returns
        -------
        Meta
            Model metadata

        Raises
        ------
        FileNotFoundError
            Raises if failed to find the model with slug specified
        RuntimeError
            If found more than one metadata files in the specified
            model folder
        """
        name = self._parse_model_name(model)
        return self._read_meta_by_name(name)

    def load_artifact_paths(self, model: Union[int, str]) -> Dict[str, List[str]]:
        """
        Returns full paths to the files and artifacts of the model

        Parameters
        ----------
        model : Union[int, str]
            Model slug or number

        Returns
        -------
        Dict[str, List[str]]
            Lists of files under the keys "artifacts" and "files"
        """
        name = self._parse_model_name(model)
        model_folder = os.path.join(self._root, name)

        result = {"artifacts": [], "files": []}
        artifact_path = os.path.join(model_folder, "artifacts")
        if os.path.exists(artifact_path):
            result["artifacts"] = [
                os.path.join(self._root, "artifacts", name)
                for name in os.listdir(artifact_path)
            ]
        file_path = os.path.join(model_folder, "files")
        if os.path.exists(file_path):
            result["files"] = [
                os.path.join(self._root, "files", name)
                for name in os.listdir(file_path)
            ]
        return result

    def save(self, model: Model, only_meta: bool = False) -> None:
        """
        Saves a model and its metadata to a line's folder.

        Model is automatically assigned a number and a model is saved
        using Model's method ``save`` in its own folder.
        Folder's name is assigned using ``f'{idx:0>5d}'``. For example: ``00001`` or ``00042``.

        It is Model's responsibility to correctly assign extension and save its own state.

        Additionally, saves ModelLine's meta to the Line's root.

        Parameters
        ----------
        model: Model
            Model to be saved
        only_meta: bool, optional
            Flag, that indicates whether to save model's artifacts.
            If True saves only metadata and wrapper.
        """

        if len(self._model_names) == 0:
            idx = 0
        else:
            idx = int(max(self._model_names)) + 1

        # Should check just in case
        while True:
            folder_name = self._model_name_by_num(idx)
            model_folder = os.path.join(self._root, folder_name)
            if os.path.exists(model_folder):
                idx += 1
                continue

            os.makedirs(model_folder)
            break

        full_path = os.path.join(self._root, folder_name)
        slug = generate_slug()
        with open(os.path.join(self._root, folder_name, "SLUG"), "w") as f:
            f.write(slug)
        self._slug2name_cache[slug] = folder_name

        meta = model.get_meta()
        meta[0]["path"] = full_path
        meta[0]["slug"] = slug
        meta[0]["saved_at"] = pendulum.now(tz="UTC")
        meta[0]["python_version"] = get_python_version()
        meta[0]["user"] = getuser()
        meta[0]["host"] = socket.gethostname()

        git_commit = get_latest_commit_hash()
        if git_commit is not None:
            meta[0]["cwd"] = os.getcwd()
            meta[0]["git_commit"] = git_commit

        git_uncommitted = get_uncommitted_changes()
        if git_uncommitted is not None:
            meta[0]["git_uncommitted_changes"] = git_uncommitted

        model_tb = None
        try:
            model.save(full_path)
        except Exception as e:
            model_exception = str(e)
            model_tb = traceback.format_exc()
            print(f"Failed to save model {full_path}\n{model_exception}\n{model_tb}")

        artifact_tb = None
        if not only_meta:
            artifacts_folder = os.path.join(full_path, "artifacts")
            os.makedirs(artifacts_folder)
            try:
                model.save_artifact(artifacts_folder)
            except Exception as e:
                artifact_exception = str(e)
                artifact_tb = traceback.format_exc()
                print(
                    f"Failed to save artifact {full_path}\n{artifact_exception}\n{artifact_tb}"
                )

        if model_tb is not None or artifact_tb is not None:
            meta[0]["errors"] = {}
            if model_tb is not None:
                meta[0]["errors"]["save"] = model_tb
            if artifact_tb is not None:
                meta[0]["errors"]["save_artifact"] = artifact_tb

        MetaHandler.write(os.path.join(full_path, "meta" + self._meta_fmt), meta)
        self._model_names.append(folder_name)
        self.sync_meta()

    def __repr__(self) -> str:
        return f"ModelLine of {len(self)} models of {self._model_cls}"

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root,
                "model_cls": repr(self._model_cls),
                "len": len(self),
                "type": "line",
                "cascade_version": __version__,
            }
        )
        return meta

    def _save_only_meta(self, model: Model) -> None:
        self.save(model, only_meta=True)

    def create_model(self, *args: Any, log_: bool = True, **kwargs: Any) -> Any:
        """
        Creates a model using the class given on
        creation, registers log callbacks for it
        and returns

        Parameters
        ----------
        log_: bool, optional
            Whether to register log callback at creation that
            saves model with ``only_meta``. By default True

        Returns
        -------
        Any
            Created and prepared model
        """
        model = self._model_cls(*args, **kwargs)
        if log_:
            model.add_log_callback(self._save_only_meta)
        return model

    def get_model_names(self) -> List[str]:
        """
        Returns names of folders models live in

        Returns
        -------
        List[str]
            Only names of folders without whole path
        """
        return self._model_names
