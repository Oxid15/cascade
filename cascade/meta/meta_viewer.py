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
from typing import Any, Dict, Union

from ..base import MetaFromFile, MetaIOError, MetaHandler, supported_meta_formats


class MetaViewer:
    """
    The class to view all metadata in folders and subfolders.
    """

    def __init__(self, root: str, filt: Union[Dict[Any, Any], None] = None) -> None:
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

        self.names = []
        for root, _, files in os.walk(self._root):
            self.names += [
                os.path.join(root, name)
                for name in files
                if os.path.splitext(name)[-1] in supported_meta_formats
            ]
        self.names = sorted(self.names)

        if filt is not None:
            self.names = list(filter(self._filter, self.names))

    def __getitem__(self, index: int) -> MetaFromFile:
        """
        Returns
        -------
        meta: MetaFromFile
            Meta object that was read from file
        """
        return MetaHandler.read(self.names[index])

    def __len__(self) -> int:
        return len(self.names)

    def write(self, path: str, obj: Any) -> None:
        """
        Dumps obj to path
        """
        warnings.warn(
            "This method will be deprecated in future versions. \
            Consider using MetaHandler instead."
        )
        MetaHandler.write(path, obj)

    def read(self, path: str) -> MetaFromFile:
        """
        Loads object from path
        """
        warnings.warn(
            "This method will be deprecated in future versions. \
            Consider using MetaHandler instead."
        )
        return MetaHandler.read(path)

    def _filter(self, name: str) -> bool:
        try:
            meta = MetaHandler.read(name)
        except MetaIOError as e:
            warnings.warn(str(e))
            return False

        if isinstance(meta, list):
            meta = meta[0]

        for key in self._filt:
            if key not in meta:
                warnings.warn(
                    f"'{key}' key is not in keys\n{list(meta.keys())}\nof file {name}"
                )
                return False

            if self._filt[key] != meta[key]:
                return False
        return True
