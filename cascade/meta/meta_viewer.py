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
import warnings
from typing import Dict, Union, Any

from ..base import MetaHandler, supported_meta_formats, Meta


class MetaViewer:
    """
    The class to view all metadata in folders and subfolders.
    """
    def __init__(self, root: str, filt: Union[Dict[str, Any], None] = None) -> None:
        """
        Parameters
        ----------
        root: str
            path to the folder containing metadata files
        filt: Dict, optional
            dictionary that specifies which values that should be present in meta
            for example to find all models use `filt={'type': 'model'}`

        See also
        --------
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
                           for name in files
                           if os.path.splitext(name)[-1] in supported_meta_formats]
        self.names = sorted(self.names)

        if filt is not None:
            self.names = list(filter(self._filter, self.names))

    def __getitem__(self, index: int) -> Meta:
        """
        Returns
        -------
        meta: List[Dict]
            Meta object
        """
        return self._mh.read(self.names[index])

    def __len__(self) -> int:
        return len(self.names)

    def write(self, path: str, obj: Meta) -> None:
        """
        Dumps obj to path
        """
        warnings.warn('This method will be deprecated in future versions. \
            Consider using MetaHandler instead.')
        self._mh.write(path, obj)

    def read(self, path: str) -> Meta:
        """
        Loads object from path
        """
        warnings.warn('This method will be deprecated in future versions. \
            Consider using MetaHandler instead.')
        return self._mh.read(path)

    def _filter(self, name: str) -> bool:
        meta = self._mh.read(name)
        meta = meta[0]  # Takes first meta which is last model's meta
        for key in self._filt:
            if key not in meta:
                raise KeyError(f"'{key}' key is not in\n{meta}")

            if self._filt[key] != meta[key]:
                return False
        return True
