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

from typing import Any, Tuple

from numpy import unique, min
from tqdm import trange

from ..data import SizedDataset, Sampler


class UnderSampler(Sampler):
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
    def __init__(self, dataset: SizedDataset[Tuple[Any, Any]], *args: Any, **kwargs: Any) -> None:
        labels = [int(dataset[i][1]) for i in trange(len(dataset))]
        ulabels, counts = unique(labels, return_counts=True)
        min_count = min(counts)

        self._rem_indices = []
        for label in ulabels:
            k = 0
            for _ in range(min_count):
                while labels[k] != label:
                    k += 1
                self._rem_indices.append(k)
                k += 1

        ln = len(self._rem_indices)
        print(f'Original length was {len(dataset)} and new is {ln}')
        super().__init__(dataset, ln, *args, **kwargs)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        idx = self._rem_indices[index]
        return self._dataset[idx]

    def __len__(self) -> int:
        return len(self._rem_indices)
