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

from . import Dataset, Modifier, T
from numpy import ceil


class SequentialCacher(Modifier):
    """
    A batched version of BruteforceCacher class.

    On first `__getitem__` call loads a batch of length `batch_size` and until indices are in the same batch doesn't
    load anything. When index misses a cached batch, then a new one is loaded.

    See also
    --------
    BruteforceCacher
    """
    def __init__(self, dataset: Dataset, batch_size=2) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            dataset to cache sequentially
        batch_size: int, default: 2
            a number of items to load and keep in each moment
        """
        # TODO: make something to release this assert
        assert hasattr(dataset, '__len__'), 'Dataset should have __len__'
        super().__init__(dataset)
        self.bs = batch_size
        self.num_batches = int(ceil(len(self._dataset) / self.bs))
        self.index = -1
        self.batch = None

    def _load(self, index) -> None:
        del self.batch
        self.batch = []

        start = index * self.bs
        end = min(start + self.bs, len(self._dataset))

        for i in range(start, end):
            self.batch.append(self._dataset[i])

        self.index += 1

    def __getitem__(self, index) -> T:
        batch_index = index // self.bs
        in_batch_idx = index % self.bs

        if batch_index != self.index:
            self._load(batch_index)

        return self.batch[in_batch_idx]
