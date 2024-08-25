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

from typing import Any, Callable

from .dataset import Dataset, IteratorDataset
from .modifier import IteratorModifier, Sampler


class Filter(Sampler):
    """
    Filter for Datasets with length. Uses a function
    to create a mask of items that will remain
    """

    def __init__(self, dataset: Dataset, filter_fn: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Filter a dataset using a filter function.
        Does not accumulate items in memory, will store only an index mask.

        Parameters
        ----------
        dataset: Dataset
            A dataset to filter
        filter_fn: Callable
            A function to be applied to every item of a dataset -
            should return bool. Will be called on every item on ``__init__``.

        Raises
        ------
        RuntimeError
            If ``filter_fn`` raises an exception
        """
        self._mask = []
        for i in range(len(dataset)):
            try:
                result = filter_fn(dataset[i])
                if result:
                    self._mask.append(i)
            except Exception as e:
                raise RuntimeError(f"Error when filtering dataset on index: {i}") from e
        super().__init__(dataset, len(self._mask), *args, **kwargs)

    def __getitem__(self, index: Any):
        return self._dataset[self._mask[index]]


class IteratorFilter(IteratorModifier):
    """
    Filter for datasets without length

    Does not filter on init, returns only items that pass the filter
    """
    def __init__(
        self, dataset: IteratorDataset, filter_fn: Callable, *args: Any, **kwargs: Any
    ) -> None:
        self._filter_fn = filter_fn
        super().__init__(dataset, *args, **kwargs)

    def __next__(self):
        while True:
            item = next(self._dataset)
            try:
                result = self._filter_fn(item)
                if result:
                    return item
            except Exception as e:
                raise RuntimeError("Error when filtering iterator") from e
