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
import traceback
from typing import Any, Dict, List, Literal, Optional, Type, Union

import pendulum

from ..base import MetaFromFile, MetaHandler, PipeMeta, TraceableOnDisk
from ..base.utils import generate_slug
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
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        All models in line should be instances of the same class.
        """

        self._slug2name_cache = dict()
        super().__init__(root, *args, **kwargs)

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
        model = super().load(num)
        if not only_meta:
            model.load_artifact(
                os.path.join(self._root, self._item_names[num], "artifacts")
            )

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
        using Model's method `save` in its own folder.
        Folder's name is assigned using f'{idx:0>5d}'. For example: 00001 or 00042.

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

        if len(self._item_names) == 0:
            idx = 0
        else:
            idx = int(max(self._item_names)) + 1

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
        self._item_names.append(folder_name)
        self.sync_meta()

    def get_meta(self) -> PipeMeta:
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
        creation, registers log callbacks for it
        and returns

        Returns
        -------
        Any
            Created and prepared model
        """
        return super().create_item(*args, **kwargs)

    def load_model_meta(self, path_spec: Union[str, int]) -> MetaFromFile:
        return super().load_obj_meta(path_spec)

    def get_model_names(self) -> List[str]:
        return super().get_item_names()
