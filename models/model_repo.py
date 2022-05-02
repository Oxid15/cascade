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
import shutil

from .model_line import ModelLine


class ModelRepo:
    """
    An interface to manage experiments with several lines of models.
    When created, initializes an empty folder constituting a repository of model lines.

    Example
    -------
    >>> from cascade.models import ModelRepo
    >>> repo = ModelRepo('repo')
    >>> vgg16_line = repo.add_line('vgg16', VGG16Model)
    >>> vgg16 = VGG16Model()
    >>> vgg16.fit()
    >>> vgg16_line.save(vgg16)


    >>> from cascade.models import ModelRepo
    >>> repo = ModelRepo('repo', lines=[dict(name='vgg16', cls=VGGModel)])
    >>> vgg16 = VGG16Model()
    >>> vgg16.fit()
    >>> repo['vgg16'].save(vgg16)

    """
    def __init__(self, folder, lines=None, meta_prefix=None, overwrite=False):
        """
        Parameters
        ----------
        folder:
            Path to a folder where ModelRepo needs to be created or already was created
            if folder does not exist, creates it
        lines: List[Dict]
            A list with parameters of model lines to add at creation or to initialize (alias for `add_model`)
        meta_prefix: Dict
            a dict that is used to update resulting meta before saving
        overwrite: bool
            if True will remove folder that is passed in first argument and start a new repo
            in that place
        See also
        --------
        cascade.models.ModelLine
        """
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.root = folder

        if overwrite and os.path.exists(self.root):
            shutil.rmtree(folder)

        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.lines = {name: ModelLine(os.path.join(self.root, name),
                                          meta_prefix=self.meta_prefix)
                          for name in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, name))}
        else:
            os.mkdir(self.root)
            self.lines = dict()

        if lines is not None:
            for line in lines:
                self.add_line(line['name'], line['cls'])

    def add_line(self, name, model_cls):
        """
        Adds new line to repo if it doesn't exist and returns it
        If line exists, defines it in repo
        Parameters
        ----------
        model_cls:
            A class of models in line. ModelLine uses this class to reconstruct a model
        name:
            Line's name
       """
        assert type(model_cls) == type, f'You should pass model\'s class, not {type(model_cls)}'

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

    def __len__(self) -> int:
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self.lines)

    def __repr__(self) -> str:
        rp = f'ModelRepo in {self.root} of {len(self)} lines'
        return ', '.join([rp] + [repr(line) for line in self.lines])
