from typing import Any, List, Sequence, Generator

import numpy as np

from ..data import T


class SimpleDataloader:
    """
    Simple batch builder - given a sequence and a size of batch
    breaks it in the subsequences
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
