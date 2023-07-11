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

from typing import Any

from numpy import ceil

from . import Modifier, SizedDataset, T


class SequentialCacher(Modifier):
    """
    A batched version of BruteforceCacher class.

    On first `__getitem__` call loads a batch of length `batch_size` and until
    indices are in the same batch doesn't
    load anything. When index misses a cached batch, then a new one is loaded.

    See also
    --------
    BruteforceCacher
    """

    def __init__(
        self, dataset: SizedDataset[T], batch_size: int = 2, *args: Any, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            Dataset to cache sequentially
        batch_size: int, optional
            A number of items to load and keep in each moment
        """

        assert hasattr(dataset, "__len__"), "Dataset should have __len__"
        super().__init__(dataset, *args, **kwargs)
        self._bs = batch_size
        self._num_batches = int(ceil(len(self._dataset) / self._bs))
        self._index = -1
        self._batch = None

    def _load(self, index: int) -> None:
        del self._batch
        self._batch = []

        start = index * self._bs
        end = min(start + self._bs, len(self._dataset))

        for i in range(start, end):
            self._batch.append(self._dataset[i])

        self._index += 1

    def __getitem__(self, index: int) -> T:
        batch_index = index // self._bs
        in_batch_idx = index % self._bs

        if batch_index != self._index:
            self._load(batch_index)

        return self._batch[in_batch_idx]
