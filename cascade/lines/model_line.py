"""
Copyright 2022-2026 Ilia Moiseev

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

import importlib
import importlib.util
import os
import socket
import sys
import traceback
from getpass import getuser
from types import ModuleType
from typing import Any, Dict, List, Optional, Type, Union

import pendulum
from typing_extensions import Literal

from ..base import Meta, MetaHandler
from ..base.utils import (
    generate_slug,
    get_latest_commit_hash,
    get_python_version,
    get_uncommitted_changes,
)
from ..models.model import Model
from .disk_line import DiskLine


class ModelLine(DiskLine):
    """
    A manager for a line of models. Used by Repo to access models on disk.
    A line of models is typically models with the same hyperparameters and architecture,
    but different epochs or trained using different data.
    """

    def __init__(
        self,
        root: str,
        model_cls: Type[Any] = Model,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        All models in line should be instances of the same class.
        """

        self._slug2name_cache = {}
        super().__init__(root, *args, item_cls=model_cls, meta_fmt=meta_fmt, **kwargs)

    def _item_name_by_num(self, num: int) -> str:
        return f"{num:0>5d}"

    def _find_name_by_slug(self, slug: str) -> Optional[str]:
        if slug in self._slug2name_cache:
            return self._slug2name_cache[slug]

        for name in self._item_names:
            filepath = os.path.join(self._root, name, "SLUG")
            if not os.path.exists(filepath):
                continue
            with open(filepath, "r") as f:
                slug_from_file = f.read()
                self._slug2name_cache[slug_from_file] = name
                if slug == slug_from_file:
                    return name

    def _parse_item_name(self, item: Union[int, str]) -> str:
        if isinstance(item, str):
            name = self._find_name_by_slug(item)
            if not name:
                raise FileNotFoundError(
                    f"Failed to find a model with slug={item} in line {self._root}"
                )
            return name
        else:
            return super()._parse_item_name(item)

    @staticmethod
    def _import_from_path(module_name: str, file_path: str) -> ModuleType:
        """
        Imports a module from file. If module is not part of the package
        just imports the file by path directly.
        If module is a part of a package with __init__.py that is on
        sys.path, then imports the whole package.

        Parameters
        ----------
        module_name : str
            Module name
        file_path : str
            Absolute module path

        Returns
        -------
        ModuleType
            Imported module

        Raises
        ------
        RuntimeError
            Can be raised if failed to get spec from path, for example
            when the path does not exist
        ImportError
            When tried to import a module from a path that is different
            from what was saved in meta
        """

        for search_path in sys.path:
            search_root = os.path.abspath(search_path or os.getcwd())

            try:
                relative_path = os.path.relpath(file_path, search_root)
            except ValueError:
                continue

            path_parts = relative_path.split(os.sep)
            if path_parts[0] == os.pardir or not path_parts[-1].endswith(".py"):
                continue

            package_parts = path_parts[:-1]
            if not package_parts or not all(
                os.path.isfile(
                    os.path.join(search_root, *package_parts[:index], "__init__.py")
                )
                for index in range(1, len(package_parts) + 1)
            ):
                continue

            module_stem, _ = os.path.splitext(path_parts[-1])

            # Import package if it has __init__ or import a module
            import_parts = (
                package_parts
                if module_stem == "__init__"
                else package_parts + [module_stem]
            )
            import_name = ".".join(import_parts)

            module = importlib.import_module(import_name)

            imported_file_path = getattr(module, "__file__", None)
            if imported_file_path and os.path.samefile(imported_file_path, file_path):
                return module

            raise ImportError(
                f"Tried to import {import_name} from {imported_file_path}, but expected {file_path}"
            )

        spec = importlib.util.spec_from_file_location(module_name, file_path)

        # They could return None if the file does not exist
        if spec is None:
            raise RuntimeError(
                f"Failed to get module spec when autoimporting {module_name} from {file_path}"
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def load(self, num: Union[int, str]) -> Model:
        """
        Loads a model using its num or slug.
        If model_cls was provided at creation will use it
        to load a model. If not, it will try to autoimport
        a class using module path from meta.

        Parameters
        ----------
        num : Union[int, str]
            Model number in line or model slug

        Returns
        -------
        Model
            Loaded model instance

        Raises
        ------
        KeyError
            If model_cls was not set in init and the model's meta does not have
            ``module_file`` or ``class`` keys.
        """
        model_name = self._parse_item_name(num)
        model_path = os.path.join(self._root, model_name)

        if self._item_cls != Model:
            model = self._item_cls.load(model_path)
        else:
            # This should work for models saved after 0.19.0
            meta = self._read_meta_by_name(model_name)

            # For models saved before
            if "module_file" not in meta[0] or "class" not in meta[0]:
                raise KeyError(
                    f"Failed to load model {num}. Tried to pull model's class and module from"
                    " meta, but didn't find `module_file` or `class` keys which were added"
                    " starting from 0.19.0."
                    " Consider using ModelLine(model_cls=YourModelClass) instead."
                )

            module_path = meta[0]["module_file"]
            cls_name = meta[0]["class"]

            # This can happen when inspect.getfile() fails inside Model
            if module_path is None:
                raise ValueError(
                    f"Failed to load model {num}. Tried to pull model's module file"
                    " from meta, but `module_file` was None. Looks like ModelLine failed to find"
                    " the module when saving."
                    " Consider importing your model's class manually and load the model"
                    " using ModelLine(model_cls=YourModelClass)"
                )

            module_name, _ = os.path.splitext(os.path.basename(module_path))
            module = self._import_from_path(module_name, module_path)
            model_cls = getattr(module, cls_name)

            model = model_cls.load(model_path)

        model.load_artifact(os.path.join(model_path, "artifacts"))
        return model

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
        name = self._parse_item_name(model)
        model_folder = os.path.join(self._root, name)

        result = {"artifacts": [], "files": []}
        artifact_path = os.path.join(model_folder, "artifacts")
        if os.path.exists(artifact_path):
            result["artifacts"] = [
                os.path.join(model_folder, "artifacts", name)
                for name in os.listdir(artifact_path)
            ]
        file_path = os.path.join(model_folder, "files")
        if os.path.exists(file_path):
            result["files"] = [
                os.path.join(model_folder, "files", name)
                for name in os.listdir(file_path)
            ]
        return result

    def save(self, model: Model, only_meta: bool = False) -> None:
        """
        Saves a model and its metadata into a model's folder

        Model is automatically assigned a number and a slug
        then it is saved using its own method ``save``.

        Folder names are assigned using f'{idx:0>5d}'. For example: 00001 or 00042.

        It is Model's responsibility to save its own state given a folder.

        Also saves ModelLine's meta to the Line's root.

        Parameters
        ----------
        model: Model
            Model to be saved
        only_meta: bool, optional
            Flag, that indicates whether to save model's artifacts.
            If True saves only metadata
        """
        meta = model.get_meta()
        obj_type = meta[0].get("type")
        if obj_type != "model":
            raise ValueError(
                f"Can only save meta of type model into ModelLine, got {obj_type}"
            )

        if len(self._item_names) == 0:
            idx = 0
        else:
            idx = int(max(self._item_names)) + 1

        # Should check just in case
        while True:
            folder_name = self._item_name_by_num(idx)
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

        meta[0]["path"] = full_path
        meta[0]["slug"] = slug
        meta[0]["saved_at"] = pendulum.now(tz="UTC")
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

        model_tb = None
        artifact_tb = None
        if not only_meta:
            try:
                model.save(full_path)
            except Exception as e:
                model_exception = str(e)
                model_tb = traceback.format_exc()
                print(
                    f"Failed to save model {full_path}\n{model_exception}\n{model_tb}"
                )

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
        self._item_names.append(folder_name)
        self.sync_meta()

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "type": "model_line",
            }
        )
        return meta

    def create_model(self, *args: Any, **kwargs: Any) -> Model:
        """
        Creates a model using the class given on line's
        creation, registers default log callback for it
        and returns. Passes all args to the object constructor.

        Returns
        -------
        Any
            Created and prepared model
        """
        model = self._item_cls(*args, **kwargs)
        model.add_log_callback(self._save_only_meta)
        return model

    def load_model_meta(self, path_spec: Union[str, int]) -> Meta:
        """
        Given a model num or a slug, loads its metadata from disk.
        Alias for ``load_obj_meta``

        Parameters
        ----------
        path_spec : Union[str, int]
            Can be an int number or a str slug

        Returns
        -------
        Meta
            Model's meta

        Raises
        ------
        FileNotFoundError
            When the num or the slug was not found in the line
        """
        return super().load_obj_meta(path_spec)

    def get_model_names(self) -> List[str]:
        """
        Get the list of model names, which are
        folder names relative to line's root

        Returns
        -------
        List[str]
            The list of names
        """
        return super().get_item_names()
