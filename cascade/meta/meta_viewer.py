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
from typing import List, Dict, Union
from ..base import MetaHandler, JSONEncoder


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
        assert os.path.exists(root)
        self.root = root
        self.filt = filt
        self.mh = MetaHandler()

        names = []
        for root, _, files in os.walk(self.root):
            names += [os.path.join(root, name) for name in files if os.path.splitext(name)[-1] == '.json']
        names = sorted(names)

        self.metas = []
        for name in names:
            self.metas.append(self.mh.read(name))
        if filt is not None:
            self.metas = list(filter(self._filter, self.metas))

    def __getitem__(self, index) -> List[Dict]:
        """
        Returns
        -------
        meta: List[Dict]
            object containing meta
        """
        return self.metas[index]

    def __len__(self) -> int:
        return len(self.metas)

    def __repr__(self) -> str:
        def pretty(d, indent=0, sep=' '):
            out = ''
            for key in d:
                if isinstance(d, dict):
                    value = d[key]
                    out += sep * indent + str(key) + ':\n'
                else:
                    value = key
                if isinstance(value, dict) or isinstance(value, list):
                    out += pretty(value, indent + 1)
                else:
                    out += sep * (indent + 1) + str(value) + sep
                    out += '\n'
            return out

        out = f'MetaViewer at {self.root}:\n'
        for i, meta in enumerate(self.metas):
            out += '-' * 20 + '\n'
            out += f'  Meta {i}:\n'
            out += '-' * 20 + '\n'
            out += pretty(meta, 4)
        return out

    def write(self, name, obj: List[Dict]) -> None:
        """
       Dumps obj to name
       """
        self.metas.append(obj)
        self.mh.write(name, obj)

    def read(self, path) -> List[Dict]:
        """
        Loads object from path
        """
        return self.mh.read(path)

    def _filter(self, meta):
        meta = meta[-1]  # Takes last meta
        for key in self.filt:
            if key not in meta:
                raise KeyError(f"'{key}' key is not in\n{meta}")
            
            if self.filt[key] != meta[key]:
                return False
        return True

    def obj_to_dict(self, obj):
        return JSONEncoder().obj_to_dict(obj)
