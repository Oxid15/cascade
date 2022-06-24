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

from tqdm import tqdm, trange
from . import Dataset, Modifier, T


class BruteforceCacher(Modifier):
    """
    Unusual modifier which loads everything in memory in initialization phase
    and then returns values from cache

    See also
    --------
    Cascade.data.SequentialCacher
    """
    def __init__(self, dataset: Dataset, *args, **kwargs) -> None:
        super().__init__(dataset, *args, **kwargs)
        # forcibly calling all previous datasets in the init
        if hasattr(self._dataset, '__len__') and hasattr(self._dataset, '__getitem__'):
            self._data = [self._dataset[i] for i in trange(len(self._dataset))]
        elif hasattr(self._dataset, '__iter__'):
            self._data = [item for item in tqdm(self._dataset)]
        else:
            raise AttributeError('Input dataset must provide Mapping or Iterable interface')

    def __getitem__(self, index) -> T:
        return self._data[index]

    def __len__(self):
        return len(self._data)
