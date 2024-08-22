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

from typing import Any

from tqdm import tqdm, trange

from .dataset import BaseDataset, T
from .modifier import Modifier


class BruteforceCacher(Modifier[T]):
    """
    Special modifier that calls all previous pipeline in __init__ loading everything
    in memory.

    Examples
    --------
    >>> from cascade import data as cdd
    >>> ds = cdd.Wrapper([0 for _ in range(1000000)])
    >>> ds = cdd.ApplyModifier(ds, lambda x: x + 1)
    >>> ds = cdd.ApplyModifier(ds, lambda x: x + 1)
    >>> ds = cdd.ApplyModifier(ds, lambda x: x + 1)

    Cache heavy upstream part once

    >>> ds = cdd.BruteforceCacher(ds)

    Then pickle it

    >>> ds = cdd.Pickler('ds', ds)

    Unpickle and use further

    >>> ds = cdd.Pickler('ds')
    >>> ds = cdd.RandomSampler(ds, 1000)

    See also
    --------
    cascade.data.Pickler
    """

    def __init__(self, dataset: BaseDataset[T], *args: Any, **kwargs: Any) -> None:
        """
        Loads every item in dataset in internal list.
        """
        super().__init__(dataset, *args, **kwargs)
        # force calling all previous datasets in the init
        if hasattr(self._dataset, "__len__") and hasattr(self._dataset, "__getitem__"):
            self._data = [self._dataset[i] for i in trange(len(self._dataset))]
        elif hasattr(self._dataset, "__iter__"):
            self._data = [item for item in tqdm(self._dataset)]
        else:
            raise AttributeError(
                "Input dataset must provide __len__ and __getitem__ or __iter__"
            )

    def __getitem__(self, index: int) -> T:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)
