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

from numpy.random import shuffle
from . import Dataset, Sampler


class RandomSampler(Sampler):
    """
    Shuffles dataset. Can randomly sample from dataset 
    if num_samples is not None and less than length of dataset.
    """
    def __init__(self, dataset: Dataset, num_samples=None, **kwargs) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            Input dataset to sample from
        num_samples: int, optional
            Should be less than len(dataset), but oversampling can be added in the future.
            If None, then just shuffles the dataset.
        """
        if num_samples is None:
            num_samples = len(dataset)
        super().__init__(dataset, num_samples, **kwargs)
        self.indices = [i for i in range(len(dataset))]
        shuffle(self.indices)
        self.indices = self.indices[:num_samples]

    def __getitem__(self, index):
        return super().__getitem__(self.indices[index])
