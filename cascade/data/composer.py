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


from typing import List, Tuple, Any

from . import SizedDataset
from ..base import PipeMeta


class Composer(SizedDataset):
    """
    Unifies two or more datasets element-wise.

    Example
    -------
    >>> from cascade import data as cdd
    >>> items = cdd.Wrapper([0, 1, 2, 3, 4])
    >>> labels = cdd.Wrapper([1, 0, 0, 1, 1])
    >>> ds = cdd.Composer((items, labels))
    >>> assert ds[0] == (0, 1)
    """
    def __init__(self, datasets: List[SizedDataset[Any]], *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        datasets: Iterable[Dataset]
            Datasets of the same length to be unified
        """
        super().__init__(*args, **kwargs)
        self._validate_input(datasets)
        self._datasets = datasets
        # Since we checked the same length in all datasets, we can
        # set the length of any dataset as the length of Composer
        self._len = len(self._datasets[0])

    def _validate_input(self, datasets: List[SizedDataset[Any]]) -> None:
        lengths = [len(ds) for ds in datasets]
        first = lengths[0]
        if not all([ln == first for ln in lengths]):
            raise ValueError(
                f'The datasets passed should be of the same length\n'
                f'Actual lengths: {lengths}'
            )

    def __getitem__(self, index: int) -> Tuple[Any]:
        return tuple(ds[index] for ds in self._datasets)

    def __len__(self) -> int:
        return self._len

    def get_meta(self) -> PipeMeta:
        """
        Composer calls `get_meta()` of all its datasets
        """
        meta = super().get_meta()
        meta[0]['data'] = [ds.get_meta() for ds in self._datasets]
        return meta
