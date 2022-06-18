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

from typing import Any, Callable
from tqdm import tqdm

from ..data import Dataset, Modifier, T


class DataValidationException(Exception):
    pass


class Validator(Modifier):
    """
    Base class for validators. Defines basic `__init__` structure
    """
    def __init__(self, dataset: Dataset, func: Callable[[Any], bool], **kwargs) -> None:  #TODO: add **kwargs everywhere
        super().__init__(dataset, **kwargs)
        self.func = func


class AggregateValidator(Validator):
    """
    This validator accepts an aggregate function that accepts a `Dataset` and return `True` of `False`

    Example
    -------
    >>> from cascade.tests.number_dataset import NumberDataset
    >>> ds = NumberDataset([1, 2, 3, 4, 5])
    >>> ds = AggregateValidator(ds, lambda x: len(x) == 5)
    """
    def __init__(self, dataset: Dataset, func: Callable[[Dataset], bool], **kwargs) -> None:
        super().__init__(dataset, func, **kwargs)

        if not self.func(self._dataset):
            raise DataValidationException(f'{repr(self._dataset)} fails on {repr(self.func)}')
        else:
            print('OK!')


class PredicateValidator(Validator):
    """
    This validator accepts function that is applied to each item in dataset and return `True` or `False`
    Calls all previous lazy datasets in __init__

    Example
    -------
    >>> from cascade.tests.number_dataset import NumberDataset
    >>> ds = NumberDataset([1, 2, 3, 4, 5])
    >>> ds = PredicateValidator(ds, lambda x: x < 6)
    """
    def __init__(self, dataset: Dataset, func: Callable[[T], bool], **kwargs) -> None:
        super().__init__(dataset, func, **kwargs)
        bad_items = []
        for i, item in tqdm(enumerate(self._dataset), desc='Checking', leave=False):
            if not self.func(item):
                bad_items.append(i)

        if len(bad_items):
            raise DataValidationException(f'Items {bad_items} are not valid')
        else:
            print('OK!')
