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

import random
from typing import Any, Callable, Iterator, Optional

from .dataset import T
from .modifier import Modifier
from .utils import DatasetOrIterator


class ApplyModifier(Modifier[T]):
    """
    Modifier that applies a function to given dataset's items in each __getitem__ call.

    Can be applied to Iterators too.
    """

    def __init__(
        self,
        dataset: DatasetOrIterator[T],
        func: Callable[[T], Any],
        p: Optional[float] = None,
        seed: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            A dataset to modify
        func: Callable
            A function to be applied to every item of a dataset -
            each ``__getitem__`` calls ``func`` on an item obtained from a previous dataset
        p: Optional[float], by default None
            The probability [0, 1] with which to apply `func`
        seed: Optional[int], by default None
            Random seed is used when p is not None

        Examples
        --------
        >>> from cascade import data as cdd
        >>> ds = cdd.Wrapper([0, 1, 2, 3, 4])
        >>> ds = cdd.ApplyModifier(ds, lambda x: x ** 2)

        Now function will only be applied when items are retrieved

        >>> assert [item for item in ds] == [0, 1, 4, 9, 16]
        """
        super().__init__(dataset, *args, **kwargs)
        self._func = func
        self._p = p
        if seed is not None:
            random.seed(seed)

    def __getitem__(self, index: int) -> Any:
        item = self._dataset[index]
        if self._p is not None:
            rnd = random.random()
            if rnd > self._p:
                return item
            else:
                return self._func(item)
        else:
            return self._func(item)

    def __iter__(self) -> Iterator[T]:
        for item in self._dataset:
            if self._p is not None:
                rnd = random.random()
                if rnd > self._p:
                    yield item
                else:
                    yield self._func(item)
            else:
                yield self._func(item)
