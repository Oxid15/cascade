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

from typing import Any, Union
from numpy.random import random_integers, shuffle
from . import SizedDataset, Sampler, T


class RandomSampler(Sampler):
    """
    Shuffles dataset. Can randomly sample from dataset
    if num_samples is not None and less than length of dataset.
    """
    def __init__(self, dataset: SizedDataset[T], num_samples: Union[int, None] = None,
                 *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            Input dataset to sample from
        num_samples: int, optional
            If less or equal than len(dataset) samples without repetitions (shuffles indices).
            If more than len(dataset) generates random integers as indices.
            If None, then just shuffles the dataset.
        """
        if num_samples is None:
            num_samples = len(dataset)
        if num_samples <= len(dataset):
            self._indices = [i for i in range(len(dataset))]
            shuffle(self._indices)
            self._indices = self._indices[:num_samples]
        else:
            self._indices = random_integers(0, len(dataset) - 1, num_samples)
        super().__init__(dataset, num_samples, **kwargs)

    def __getitem__(self, index: int) -> T:
        return super().__getitem__(self._indices[index])
