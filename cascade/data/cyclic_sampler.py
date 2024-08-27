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

from typing import Iterator

from .dataset import T
from .modifier import Sampler


class CyclicSampler(Sampler[T]):
    """
    A Sampler that iterates ``num_samples`` times through an input Dataset in cyclic manner

    Example
    -------
    >>> from cascade.data import CyclicSampler, Wrapper
    >>> ds = Wrapper([1,2,3])
    >>> ds = CyclicSampler(ds, 7)
    >>> assert [item for item in ds] == [1, 2, 3, 1, 2, 3, 1]
    """

    def __getitem__(self, index: int) -> T:
        internal_index = index % len(self._dataset)
        return self._dataset[internal_index]

    def __iter__(self) -> Iterator[T]:
        for index in range(super().__len__()):
            yield self.__getitem__(index)
