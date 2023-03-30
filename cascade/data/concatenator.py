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

from typing import List, Any

import numpy as np
from .dataset import SizedDataset, T
from ..base import PipeMeta


class Concatenator(SizedDataset):
    """
    Unifies several Datasets under one, calling them sequentially in the provided order.

    Examples
    --------
    >>> from cascade.data import Wrapper, Concatenator
    >>> ds_1 = Wrapper([0, 1, 2])
    >>> ds_2 = Wrapper([2, 1, 0])
    >>> ds = Concatenator((ds_1, ds_2))
    >>> assert [item for item in ds] == [0, 1, 2, 2, 1, 0]
    """
    def __init__(self, datasets: List[SizedDataset[T]], *args: Any, **kwargs: Any) -> None:
        """
        Creates concatenated dataset from the list of datasets provided

        Parameters
        ----------
        datasets: Union[Iterable[Dataset], Mapping[Dataset]]
            A list or tuple of datasets to concatenate
        """
        self._datasets = datasets
        lengths = [len(ds) for ds in self._datasets]
        self._shifts = np.cumsum([0] + lengths)
        super().__init__(*args, **kwargs)

    def __getitem__(self, index: int) -> T:
        ds_index = 0
        for sh in self._shifts[1:]:
            if index >= sh:
                ds_index += 1
        return self._datasets[ds_index][index - self._shifts[ds_index]]

    def __len__(self) -> int:
        """
        Length of Concatenator is a sum of lengths of its datasets
        """
        return sum([len(ds) for ds in self._datasets])

    def __repr__(self) -> str:
        """
        Mentions joined datasets in its repr in form:
        Concatenator of
        Dataset1
        Dataset2
        ...
        """
        rp = super().__repr__()
        return f'{rp} of\n' + '\n'.join(repr(ds) for ds in self._datasets)

    def get_meta(self) -> PipeMeta:
        """
        Concatenator calls `get_meta()` of all its datasets
        """
        meta = super().get_meta()
        meta[0]['data'] = [ds.get_meta() for ds in self._datasets]
        return meta
