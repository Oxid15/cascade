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

from typing import Any, List, Sequence, Generator

import numpy as np

from ..data import T


class SimpleDataloader:
    """
    Simple batch builder - given a sequence and a size of batch
    breaks it in the subsequences

    >>> from cascade.data import SimpleDataloader
    >>> dl = SimpleDataloader([0, 1, 2], 2)
    >>> [item for item in dl]
    [[0, 1], [2]]

    """
    def __init__(self, data: Sequence[T], batch_size: int = 1) -> None:
        if batch_size == 0:
            raise ValueError("Batch size cannot be 0")
        if batch_size > len(data):
            raise ValueError(
                f"Batch size ({batch_size}) is larger than sequence length ({len(data)})")

        self._data = data
        self._bs = batch_size

    def __getitem__(self, index: int) -> List[Any]:
        batch = []
        start_index = index * self._bs
        end_index = min((index + 1) * self._bs, len(self._data))

        for i in range(start_index, end_index):
            item = self._data[i]
            batch.append(item)
        return batch

    def __iter__(self) -> Generator[List[Any], Any, None]:
        for i in range(len(self)):
            yield self[i]

    def __len__(self) -> int:
        return int(np.ceil(len(self._data) / self._bs))
