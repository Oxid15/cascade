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

from typing import Any, Callable

from . import Dataset, Modifier, T


class ApplyModifier(Modifier):
    """
    Modifier that maps a function to given dataset's items in a lazy way.
    """

    def __init__(
        self, dataset: Dataset[T], func: Callable[[T], Any], *args: Any, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        dataset: Dataset
            A dataset to modify
        func: Callable
            A function to be applied to every item of a dataset -
            each `__getitem__` would call `func` on an item obtained from a previous dataset

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

    def __getitem__(self, index: int) -> Any:
        item = self._dataset[index]
        return self._func(item)
