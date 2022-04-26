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
import datetime
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
    def __init__(self, folder, model_cls=Model, meta_prefix=None):
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
            a dict that is used to update resulting meta before saving

        See also
        --------
        cascade.models.ModelRepo
        """
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.model_cls = model_cls
        self.root = folder
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.model_names = [name for i, name in enumerate(sorted(os.listdir(self.root)))
                                if not name.endswith('.json')]
        else:
            os.mkdir(self.root)
            self.model_names = []
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

    def __len__(self):
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
        using Model's method `save`. Name is assigned using f'{idx:0>5d}'. For example: 00001 or 00042.
        The name passed to model's save is without extension. It is Model's responsibility to correctly
        assign extension and save its state.
        """
        idx = len(self.model_names)
        only_name = f'{idx:0>5d}'
        full_path = os.path.join(self.root, only_name)
        self.model_names.append(only_name)
        model.save(full_path)

        exact_filename = glob.glob(f'{full_path}*')[0]
        with open(exact_filename, 'rb') as f:
            md5sum = md5(f.read()).hexdigest()

        meta = model.get_meta()

        meta[0].update(self.meta_prefix)
        meta[0]['name'] = exact_filename
        meta[0]['md5sum'] = md5sum
        meta[0]['saved_at'] = datetime.datetime.now()

        # TODO: save meta using another naming rule (the problem when model also uses .json)
        self.meta_viewer.write(os.path.join(self.root, f'{idx:0>5d}.json'), meta[0])

    def __repr__(self):
        return f'ModelLine of {len(self)} models'


class ModelRepo:
    """
    An interface to manage experiments with several lines of models. When created, initializes an empty folder
    constituting a repository of model lines.
    """
    def __init__(self, folder, meta_prefix=None):
        """
        All models in repo should be instances of the same class.

        Parameters
        ----------
        folder:
            Path to a folder where ModelRepo needs to be created or already was created
            if folder does not exist, creates it
        meta_prefix:
            a dict that is used to update resulting meta before saving

        See also
        --------
        cascade.models.ModelLine
        """
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.root = folder
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.lines = {name: ModelLine(os.path.join(self.root, name),
                                          meta_prefix=self.meta_prefix)
                          for name in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, name))}
        else:
            os.mkdir(self.root)
            self.lines = dict()

    def add_line(self, model_cls, name=None):
        """
        Adds new line to repo if doesn't exist and returns it

        Parameters
        ----------
        model_cls:
            A class of models in line. ModelLine uses this class to reconstruct a model
        name:
            Line's name - optional, if None assigns line_index:05d e.g. 00000, 00001, ...
       """
        if name is None:
            name = f'{len(self.lines):05d}'
        else:
            name = str(name)

        folder = os.path.join(self.root, name)
        line = ModelLine(folder, model_cls=model_cls, meta_prefix=self.meta_prefix)
        self.lines[name] = line
        return line

    def __getitem__(self, key) -> ModelLine:
        """
        Returns
        -------
        line: ModelLine
           existing line of the name passed in `key`
        """
        return self.lines[key]

    def __len__(self):
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self.lines)

    def __repr__(self):
        rp = f'ModelRepo in {self.root} of {len(self)} lines'
        return '\n'.join([rp] + [repr(line) for line in self.lines])
