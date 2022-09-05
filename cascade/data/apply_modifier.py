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

from typing import Callable
from . import Dataset, Modifier, T


class ApplyModifier(Modifier):
    """
    Modifier that maps a function to previous dataset's elements in a lazy way.
    """
    def __init__(self, dataset: Dataset, func: Callable, *args, **kwargs) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            a dataset to modify
        func: Callable
            a function to be applied to every item of a dataset -
            each `__getitem__` would call `func` on an item obtained from a previous dataset
        """
        super().__init__(dataset, *args, **kwargs)
        self._func = func

    def __getitem__(self, index: int) -> T:
        item = self._dataset[index]
        return self._func(item)

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp}, {repr(self._func)}'
