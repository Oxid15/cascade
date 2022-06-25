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
import logging
from typing import List, Dict
import shutil

import pendulum
from deepdiff.diff import DeepDiff

from ..base import Traceable
from .model_line import ModelLine
from ..meta import MetaViewer


class ModelRepo(Traceable):
    """
    An interface to manage experiments with several lines of models.
    When created, initializes an empty folder constituting a repository of model lines.
    
    Stores meta-data in file meta.json in the root folder. With every run if the repo was already
    created earlier, updates its meta and logs changes in human-readable format in file history.log

    Example
    -------
    >>> from cascade.models import ModelRepo
    >>> repo = ModelRepo('repo', meta_prefix={'description': 'This is a repo with one VGG16 line for the example.'})
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
    def __init__(self, folder, lines=None, overwrite=False, **kwargs):
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
        See also
        --------
        cascade.models.ModelLine
        """
        super().__init__(**kwargs)
        self.root = folder

        if overwrite and os.path.exists(self.root):
            shutil.rmtree(folder)

        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            # Can create MV only if path already exists
            self.meta_viewer = MetaViewer(self.root)
            self.lines = {name: ModelLine(os.path.join(self.root, name),
                                          meta_prefix=self.meta_prefix)
                          for name in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, name))}
        else:
            os.mkdir(self.root)
            # Here the same with MV
            self.meta_viewer = MetaViewer(self.root)
            self.lines = dict()

        self.logger = logging.getLogger(folder)
        hdlr = logging.FileHandler(os.path.join(self.root, 'history.log'))
        hdlr.setFormatter(logging.Formatter('\n%(asctime)s\n%(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel('DEBUG')

        if lines is not None:
            for line in lines:
                self.add_line(line['name'], line['cls'])

        self._update_meta()

    def add_line(self, name, model_cls):
        """
        Adds new line to repo if it doesn't exist and returns it
        If line exists, defines it in repo

        Additionally, updates repo's meta on disk
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

        self._update_meta()
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

    def _update_meta(self):
        # Reads meta if exists and updates it with new values
        # writes back to disk
        meta_path = os.path.join(self.root, 'meta.json')
        hist_path = os.path.join(self.root, 'history.json')

        meta = {}
        if os.path.exists(meta_path):
            meta = self.meta_viewer.read(meta_path)[0]

        self.logger.info(DeepDiff(
            meta,
            self.meta_viewer.obj_to_dict(self.get_meta()[0])).pretty()
        )

        meta.update(self.get_meta()[0])
        self.meta_viewer.write(meta_path, [meta])

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
            'root': self.root,
            'len': len(self),
            'updated_at': pendulum.now(tz='UTC'),
            'type': 'repo'
        })
        return meta
