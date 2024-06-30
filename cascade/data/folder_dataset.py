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
from typing import Any, List

from ..base import Meta, raise_not_implemented
from .dataset import Dataset, T


class FolderDataset(Dataset[T]):
    """
    Basic "folder of files" dataset. Accepts root folder in which considers all files.
    Is abstract - getitem is not defined, since it is specific for each file type.

    See also
    --------
    cascade.utils.FolderImageDataset
    """

    def __init__(self, root: str, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        root: str
            A path to the folder of files
        """
        super().__init__(*args, **kwargs)
        self._root = os.path.abspath(root)
        if not os.path.exists(self._root):
            raise FileNotFoundError(self._root)

        self._names = sorted(
            [
                os.path.join(self._root, name)
                for name in sorted(os.listdir(self._root))
                if not os.path.isdir(name)
            ]
        )

    def __getitem__(self, index: Any) -> T:
        raise_not_implemented("cascade.data.FolderDataset", "__getitem__")

    def get_names(self) -> List[str]:
        """
        Returns a list of full paths to the files
        """
        return self._names

    def get_meta(self) -> Meta:
        """
        Returns meta containing root folder
        """
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root
            }
        )
        return meta

    def __len__(self) -> int:
        return len(self._names)
