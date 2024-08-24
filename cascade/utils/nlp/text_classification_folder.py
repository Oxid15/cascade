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
from typing import Any, Tuple

import numpy as np

from ...base import Meta
from ...data.dataset import Dataset, T


class TextClassificationFolder(Dataset[T]):
    """
    Dataset to simplify loading of data for text classification.
    Texts of different classes should be placed in different folders.
    """

    # TODO: can be implemented to be ClassificationFolder and share this functionality with images?
    def __init__(
        self, path: str, encoding: str = "utf-8", *args: Any, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        path: str
            Path to the folder with folders of text files.
            In each folder should be only one class of texts.
        encoding: str, optional
            Encoding that is used to open files.
        """
        super().__init__(*args, *kwargs)
        self._encoding = encoding
        self._root = os.path.abspath(path)
        folders = os.listdir(self._root)
        self._paths = []
        self._labels = []
        for i, folder in enumerate(folders):
            files = [name for name in os.listdir(os.path.join(self._root, folder))]
            self._paths += [os.path.join(self._root, folder, f) for f in files]
            self._labels += [i for _ in range(len(files))]

        classes = [
            (folder, len(os.listdir(os.path.join(self._root, folder))))
            for folder in folders
        ]
        print(f"Found {len(folders)} classes: {classes}")

    def __getitem__(self, index: int) -> Tuple[str, int]:
        with open(self._paths[index], "r", encoding=self._encoding) as f:
            text = " ".join(f.readlines())
            label = self._labels[index]
        return text, label

    def __len__(self) -> int:
        """
        Total number of files.
        """
        return len(self._paths)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root,
                "labels": np.unique(self._labels).tolist(),
            }
        )
        return meta
