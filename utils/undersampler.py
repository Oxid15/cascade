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

from ..data import Sampler
from numpy import unique, min, histogram
from tqdm import trange


class UnderSampler(Sampler):
    def __init__(self, dataset):
        super().__init__(dataset, None)

        labels = [int(self._dataset[i][1]) for i in trange(len(self._dataset))]
        ulabels = unique(labels)
        label_nums, _ = histogram(labels, bins=len(ulabels))
        rem_nums = min(label_nums)

        self.rem_indices = []
        for label in ulabels:
            k = 0
            for _ in range(rem_nums):
                while labels[k] != label:
                    k += 1
                self.rem_indices.append(k)
        print(f'Original length was {len(self._dataset)} and new is {len(self)}')

    def __getitem__(self, index):
        idx = self.rem_indices[index]
        return self._dataset[idx]

    def __len__(self):
        return len(self.rem_indices)
