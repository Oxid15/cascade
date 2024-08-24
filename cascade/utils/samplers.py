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

from itertools import cycle
from typing import Any, Dict, Optional, Tuple

import numpy as np
from tqdm import trange

from ..base import Meta
from ..data.dataset import Dataset, T
from ..data.modifier import Sampler


class OverSampler(Sampler[T]):
    """
    Accepts datasets which return tuples of objects and labels in the respected order.
    Isn't lazy - runs through all the items ones to determine key order.
    Doesn't store values afterwards.

    To oversample it repeats items with minority labels for the amount
    of times needed to make equal distribution.
    Works for any number of classes.

    Labels are considered to be in the second place of each item that a dataset returns.

    Important
    ---------
    Sampler orders the items in the dataset.
    Consider shuffling the dataset after sampling if label order is important.
    """

    def __init__(
        self, dataset: Dataset[Tuple[Any, Any]], *args: Any, **kwargs: Any
    ) -> None:
        labels = [int(dataset[i][1]) for i in trange(len(dataset))]
        ulabels, counts = np.unique(labels, return_counts=True)
        how_much_add = np.max(counts) - counts

        self._add_indices = []
        for label_idx, label in enumerate(ulabels):
            k = 0
            for _ in range(how_much_add[label_idx]):
                while labels[k] != label:
                    k += 1
                self._add_indices.append(k)

        ln = len(dataset) + len(self._add_indices)
        print(f"Original length was {len(dataset)} and new is {ln}")

        super().__init__(dataset, num_samples=ln, *args, **kwargs)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        if index < len(self._dataset):
            return self._dataset[index]
        else:
            idx = self._add_indices[index - len(self._dataset)]
            return self._dataset[idx]

    def __len__(self) -> int:
        return len(self._dataset) + len(self._add_indices)


class UnderSampler(Sampler[T]):
    """
    Accepts datasets which return tuples of objects and labels.
    Isn't lazy - runs through all the items ones to determine key order.
    Doesn't store values in memory afterwards.

    To undersample it removes items of majority class for the amount
    of times needed to make equal distribution.
    Works for any number of classes.

    Labels are considered to be in the second place of each item that a dataset returns.

    Important
    ---------
    Sampler orders the items in the dataset.
    Consider shuffling the dataset after sampling if label order is important.
    """

    def __init__(
        self, dataset: Dataset[Tuple[Any, Any]], *args: Any, **kwargs: Any
    ) -> None:
        labels = [int(dataset[i][1]) for i in trange(len(dataset))]
        ulabels, counts = np.unique(labels, return_counts=True)
        min_count = np.min(counts)

        self._rem_indices = []
        for label in ulabels:
            k = 0
            for _ in range(min_count):
                while labels[k] != label:
                    k += 1
                self._rem_indices.append(k)
                k += 1

        ln = len(self._rem_indices)
        print(f"Original length was {len(dataset)} and new is {ln}")
        super().__init__(dataset, ln, *args, **kwargs)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        idx = self._rem_indices[index]
        return self._dataset[idx]

    def __len__(self) -> int:
        return len(self._rem_indices)


class WeighedSampler(Sampler[T]):
    """
    Samples each class certain amount of times.

    Important
    ---------
    Sampler orders the items in the dataset in such way that items with each label go in row.
    Consider shuffling the dataset after sampling if label order is important.

    Example
    -------
    >>> from cascade import data as cdd
    >>> from cascade.utils.samplers import WeighedSampler
    >>> ds = cdd.Wrapper([('item1', 0), ('item2', 1)])
    >>> ds = WeighedSampler(ds, {0: 2, 1: 1})
    >>> assert [item for item in ds] == [('item1', 0), ('item1', 0), ('item2', 1)]

    See also
    --------
    cascade.utils.OverSampler
    cascade.utils.UnderSampler
    cascade.data.RandomSampler
    """

    def __init__(
        self,
        dataset: Dataset[Tuple[Any, Any]],
        partitioning: Optional[Dict[Any, int]] = None,
    ) -> None:
        """
        Parameters
        ----------
            dataset: Dataset
                A dataset to sample
            partitioning: Dict[Any, int], optional
                A dictionary with labels as keys and the number of samples as values.
                If some label omitted, assumes that it should be sampled the same number
                of times it is actually appears in the dataset.
        """
        labels = np.asarray([dataset[i][1] for i in trange(len(dataset))])
        ulabels, counts = np.unique(labels, return_counts=True)
        # Convert to lists to prevent serialization problems with metadata
        ulabels, counts = ulabels.tolist(), counts.tolist()

        if partitioning is None:
            partitioning = {}

        self._check_partitioning(ulabels, partitioning)
        self._partitioning = partitioning

        # If label is omitted in partitioning, add it with true count
        for ulabel, count in zip(ulabels, counts):
            if ulabel not in self._partitioning:
                self._partitioning[ulabel] = count

        self._indices = []
        for label in self._partitioning:
            count = 0
            for idx in cycle(np.where(labels == label)[0]):
                if count >= self._partitioning[label]:
                    break

                self._indices.append(idx)
                count += 1

        ln = len(self._indices)
        assert ln == sum(
            partitioning.values()
        ), "The length should be equal to the sum of partitions - something went wrong"
        print(f"Original length was {len(dataset)} and new is {ln}")
        super().__init__(dataset, ln)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        idx = self._indices[index]
        return self._dataset[idx]

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["partitioning"] = self._partitioning
        return meta

    def _check_partitioning(self, ulabels, partitioning) -> None:
        """
        Checks if all labels that were passed in partitioning
        are present in dataset's unique labels
        """
        for label in partitioning:
            if label not in ulabels:
                raise ValueError(
                    f"Label {label} was not found in dataset's labels: {ulabels}"
                )
