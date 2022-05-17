"""
Copyright 2022 Ilia Moiseev

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
from typing import List, Dict
import pendulum
import glob
from hashlib import md5

from .model import Model
from ..meta import MetaViewer


class ModelLine:
    """
    A manager for a line of models. Used by ModelRepo for access to models on disk.
    A line of models is typically a models with the same hyperparameters and architecture,
    but different epochs or using different data.
    """
    def __init__(self, folder, model_cls=Model, meta_prefix=None) -> None:
        """
        All models in line should be instances of the same class.

        Parameters
        ----------
        folder:
            Path to a folder where ModelLine will be created or already was created
            if folder does not exist, creates it
        model_cls:
            A class of models in repo. ModelLine uses this class to reconstruct a model
        meta_prefix:
            a dict that is used to update resulting model line's meta before saving
        See also
        --------
        cascade.models.ModelRepo
        """
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.model_cls = model_cls
        self.root = folder
        self.model_names = []
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            for root, dirs, files in os.walk(self.root):
                model_dir = os.path.split(root)[-1]
                self.model_names \
                    += [os.path.join(model_dir, name)
                        for name in files
                        if os.path.splitext(name)[0] == 'model']
        else:
            os.mkdir(self.root)
        self.meta_viewer = MetaViewer(self.root)

    def __getitem__(self, num) -> Model:
        """
        Creates a model of `model_cls` and loads it using Model's `load` method.

        Returns
        -------
            model: Model
                a loaded model
        """
        model = self.model_cls()
        model.load(os.path.join(self.root, self.model_names[num]))
        return model

    def __len__(self) -> int:
        """
        Returns
        -------
        A number of models in line
        """
        return len(self.model_names)

    def save(self, model: Model) -> None:
        """
        Saves a model and its meta data to a line folder.
        Model is automatically assigned a number and a model is saved
        using Model's method `save` in its own folder.
        Folder's name is assigned using f'{idx:0>5d}'. For example: 00001 or 00042.
        The name passed to model's save is just "model" without extension.
        It is Model's responsibility to correctly  assign extension and save its own state.

        Additionally, saves ModelLine's meta to the Line's root
        """
        idx = len(self.model_names)
        folder_name = f'{idx:0>5d}'
        full_path = os.path.join(self.root, folder_name, 'model')
        self.model_names.append(os.path.join(folder_name, 'model'))

        os.makedirs(os.path.join(self.root, folder_name), exist_ok=True)
        model.save(full_path)

        # Find anything that matches /path/model_folder/model*
        exact_filename = glob.glob(f'{full_path}*')

        assert len(exact_filename) > 0, 'Model file was\'nt found.\n \
            It may be that Model didn\'t save itself, or the name of the file \
                didn\'t match "model*"'

        exact_filename = exact_filename[0]
        with open(exact_filename, 'rb') as f:
            md5sum = md5(f.read()).hexdigest()

        meta = model.get_meta()

        meta[-1]['name'] = exact_filename
        meta[-1]['md5sum'] = md5sum
        meta[-1]['saved_at'] = pendulum.now(tz='UTC')

        # Save model's meta
        self.meta_viewer.write(os.path.join(self.root, folder_name, 'meta.json'), meta)

        # Save updated line's meta
        self.meta_viewer.write(os.path.join(self.root, 'meta.json'), self.get_meta())

    def __repr__(self) -> str:
        return f'ModelLine of {len(self)} models of {self.model_cls}'

    def get_meta(self) -> List[Dict]:
        meta = {
            'name': repr(self),
            'root': self.root,
            'model_cls': repr(self.model_cls),
            'len': len(self),
            'updated_at': pendulum.now(tz='UTC')
        }
        meta.update(self.meta_prefix)
        return [meta]
