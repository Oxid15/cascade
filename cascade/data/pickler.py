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
import pickle
from typing import Any, Optional

from typing_extensions import deprecated

from .dataset import BaseDataset, T
from .modifier import BaseModifier


@deprecated("Pickler is deprecated since 0.14.0 and will be"
            " removed in subsequent versions. Consider using cascade.base.Cache")
class Pickler(BaseModifier[T]):
    """
    Pickles input dataset or unpickles one
    """

    def __init__(
        self,
        path: str,
        dataset: Optional[BaseDataset[T]] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Loads pickled dataset or dumps one depending on parameters passed:

        1. If only path is passed - loads dataset from path provided if path exists
        2. if path provided with a dataset dumps dataset to the path

        Parameters
        ----------
        path: str
            Path to the pickled dataset
        dataset: BaseDataset, optional
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
        with open(self._path, "wb") as f:
            pickle.dump(self._dataset, f)

    def _load(self) -> None:
        with open(self._path, "rb") as f:
            self._dataset = pickle.load(f)

    def __getitem__(self, index: int) -> T:
        """
        Forwards the call to the wrapped dataset regardless
        of presence of this method in it
        """
        return self._dataset.__getitem__(index)

    def __len__(self) -> int:
        """
        Forwards the call to the wrapped dataset regardless
        of presence of this method in it
        """
        return self._dataset.__len__()

    def ds(self) -> BaseDataset[T]:
        """
        Returns pickled dataset
        """
        return self._dataset
