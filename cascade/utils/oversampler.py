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

from ..data import T, Dataset, Sampler
import numpy as np
from tqdm import trange


class OverSampler(Sampler):
    """
    Accepts datasets which return tuples of objects and labels in the respected order.
    Isn't lazy - runs through all the items ones to determine key order.
    Doesn't store values afterwards.

    To oversample it repeats items with minority labels for the amount
    of times needed to make equal distribution.
    Works for any number of classes.
    """
    def __init__(self, dataset: Dataset, *args, **kwargs) -> None:
        labels = [int(dataset[i][1]) for i in trange(len(dataset))]
        ulabels = np.unique(labels)
        label_nums, _ = np.histogram(labels, bins=len(ulabels))
        add_nums = np.max(label_nums) - label_nums

        self._add_indices = []
        for label_idx, label in enumerate(ulabels):
            k = 0
            for _ in range(add_nums[label_idx]):
                while labels[k] != label:
                    k += 1
                self._add_indices.append(k)
        ln = len(dataset) + len(self._add_indices)
        print(f'Original length was {len(dataset)} and new is {ln}')

        super().__init__(dataset, num_samples=ln, *args, **kwargs)

    def __getitem__(self, index: int) -> T:
        if index < len(self._dataset):
            return self._dataset[index]
        else:
            idx = self._add_indices[index - len(self._dataset)]
            return self._dataset[idx]

    def __len__(self) -> int:
        return len(self._dataset) + len(self._add_indices)
