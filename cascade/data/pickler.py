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
from typing import Union, Any
import pickle
from . import Dataset, Modifier, T


class Pickler(Modifier):
    """
    Pickles input dataset or unpickles one
    """
    def __init__(self,
                 path: str,
                 dataset: Union[Dataset[T], None] = None,
                 *args: Any, **kwargs: Any) -> None:
        """
        Loads pickled dataset or dumps one depending on parameters passed:

        1. If only path is passed - loads dataset from path provided if path exists
        2. if path provided with a dataset dumps dataset to the path

        Parameters
        ----------
        path: str
            Path to the pickled dataset
        dataset: Dataset, optional
            A dataset to be pickled

        Raises
        ------
        FileNotFoundError
            if path does not exist
        """
        super().__init__(dataset, *args, **kwargs)
        self._path = path

        if self._dataset is None:
            if not os.path.exists(self._path):
                raise FileNotFoundError(self._path)
            self._load()
        else:
            self._dump()

    def _dump(self) -> None:
        with open(self._path, 'wb') as f:
            pickle.dump(self._dataset, f)

    def _load(self) -> None:
        with open(self._path, 'rb') as f:
            self._dataset = pickle.load(f)

    def ds(self) -> Dataset[T]:
        """
        Returns pickled dataset
        """
        return self._dataset
