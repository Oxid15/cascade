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
from ..base import MetaHandler, JSONEncoder, supported_meta_formats


class MetaViewer:
    """
    The class to read and write meta data.
    """
    def __init__(self, root, filt=None) -> None:
        """
        Parameters
        ----------
        root:
            path to the folder containing metadata files
            to dump and load metadata files MetaHandler is used
        filt Dict, optional:
            dictionary that specifies which values should be present in meta
            for example to find all models use `filt={'type': 'model'}`

        See also
        --------
        cascade.meta.ModelRepo
        cascade.meta.MetaHandler
        """
        if not os.path.exists(root):
            raise FileNotFoundError(root)

        self._root = root
        self._filt = filt
        self._mh = MetaHandler()

        self.names = []
        for root, _, files in os.walk(self._root):
            self.names += [os.path.join(root, name)
                           for name in files if os.path.splitext(name)[-1] in supported_meta_formats]
        self.names = sorted(self.names)

        if filt is not None:
            self.names = list(filter(self._filter, self.names))

    def __getitem__(self, index) -> List[Dict]:
        """
        Returns
        -------
        meta: List[Dict]
            object containing meta
        """
        return self.read(self.names[index])

    def __len__(self) -> int:
        return len(self.names)

    def write(self, path, obj: List[Dict]) -> None:
        """
        Dumps obj to path
        """
        self._mh.write(path, obj)

    def read(self, path) -> List[Dict]:
        """
        Loads object from path
        """
        return self._mh.read(path)

    def _filter(self, name):
        meta = self.read(name)
        meta = meta[-1]  # Takes last meta
        for key in self._filt:
            if key not in meta:
                raise KeyError(f"'{key}' key is not in\n{meta}")

            if self._filt[key] != meta[key]:
                return False
        return True

    @staticmethod
    def obj_to_dict(obj):
        return JSONEncoder().obj_to_dict(obj)
