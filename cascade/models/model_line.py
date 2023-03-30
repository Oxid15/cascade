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
from typing import Type, Literal, Any
import pendulum
import glob
from hashlib import md5

from ..base import Traceable, MetaHandler, supported_meta_formats, PipeMeta
from .model import Model


class ModelLine(Traceable):
    """
    A manager for a line of models. Used by ModelRepo for access to models on disk.
    A line of models is typically a models with the same hyperparameters and architecture,
    but different epochs or using different data.
    """
    def __init__(self, folder: str, model_cls: Type = Model,
                 meta_fmt: Literal['.json', '.yml', '.yaml'] = '.json', **kwargs: Any) -> None:
        """
        All models in line should be instances of the same class.

        Parameters
        ----------
        folder: str
            Path to a folder where ModelLine will be created or already was created.
            If folder does not exist, creates it
        model_cls: type, optional
            A class of models in line. ModelLine uses this class to reconstruct a model
        meta_fmt: str, optional
            Format in which to store meta data.
        See also
        --------
        cascade.models.ModelRepo
        """
        super().__init__(**kwargs)

        assert meta_fmt in supported_meta_formats, \
            f'Only {supported_meta_formats} are supported formats'
        self._meta_fmt = meta_fmt
        self._model_cls = model_cls
        self.root = folder
        self.model_names = []
        if os.path.exists(self.root):
            assert os.path.isdir(self.root), f'folder should be directory, got `{folder}`'
            self.model_names = sorted(
                [os.path.join(model_folder, 'model')
                    for model_folder in os.listdir(self.root)
                    if os.path.isdir(os.path.join(self.root, model_folder))])

            if len(self.model_names) == 0:
                warnings.warn(
                    f'Model folders were not found by the line in {self.root}'
                )

        else:
            # No folder -> create
            os.mkdir(self.root)
        self._mh = MetaHandler()

    def __getitem__(self, num: int) -> Model:
        """
        Creates a model of `model_cls` and loads it using Model's `load` method.

        Returns
        -------
            model: Model
                a loaded model
        """
        model = self._model_cls()
        model.load(os.path.join(self.root, self.model_names[num]))
        return model

    def __len__(self) -> int:
        """
        Returns
        -------
        A number of models in line
        """
        return len(self.model_names)

    def save(self, model: Model, only_meta: bool = False) -> None:
        """
        Saves a model and its metadata to a line's folder.
        Model is automatically assigned a number and a model is saved
        using Model's method `save` in its own folder.
        Folder's name is assigned using f'{idx:0>5d}'. For example: 00001 or 00042.
        The name passed to model's save is just "model" without extension.
        It is Model's responsibility to correctly  assign extension and save its own state.

        Additionally, saves ModelLine's meta to the Line's root.

        Parameters
        ----------
        model: Model
            Model to be saved
        only_meta: bool, optional
            Flag, that indicates whether to save model's binaries. If True saves only metadata.
        """
        idx = len(self.model_names)
        folder_name = f'{idx:0>5d}'
        full_path = os.path.join(self.root, folder_name, 'model')

        # Create model's folder if no
        os.makedirs(os.path.join(self.root, folder_name), exist_ok=True)

        # Prepare meta for saving
        meta = model.get_meta()

        if not only_meta:
            # Save model
            model.save(full_path)

            # Find anything that matches /path/model_folder/model*
            exact_filename = glob.glob(f'{full_path}*')

            assert len(exact_filename) > 0, 'Model file wasn\'t found.\n '
            'It may be that Model didn\'t save itself when save() was called,'
            'or the name of the file didn\'t match "model*"'

            exact_filename = exact_filename[0]
            with open(exact_filename, 'rb') as f:
                md5sum = md5(f.read()).hexdigest()

            meta[0]['name'] = exact_filename
            meta[0]['md5sum'] = md5sum

        meta[0]['saved_at'] = pendulum.now(tz='UTC')
        self.model_names.append(os.path.join(folder_name, 'model'))

        # Save model's meta
        self._mh.write(os.path.join(self.root, folder_name, 'meta' + self._meta_fmt), meta)

        # Save updated line's meta
        self._mh.write(os.path.join(self.root, 'meta' + self._meta_fmt), self.get_meta())

    def __repr__(self) -> str:
        return f'ModelLine of {len(self)} models of {self._model_cls}'

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({
            'root': self.root,
            'model_cls': repr(self._model_cls),
            'len': len(self),
            'updated_at': pendulum.now(tz='UTC'),
            'type': 'line'
        })
        return meta
