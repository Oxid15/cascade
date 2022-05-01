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
    def __init__(self, dataset: Dataset, func: Callable[[Any], bool]) -> None:
        super().__init__(dataset)
        self.func = func


class AggregateValidator(Validator):
    def __init__(self, dataset: Dataset, func: Callable[[Dataset], bool]) -> None:
        super().__init__(dataset, func)

        if not self.func(self._dataset):
            raise DataValidationException(f'{repr(self._dataset)} fails on {repr(self.func)}')
        else:
            print('OK!')


class PredicateValidator(Validator):
    def __init__(self, dataset: Dataset, func: Callable[[T], bool]) -> None:
        super().__init__(dataset, func)
        bad_items = []
        for i, item in tqdm(enumerate(self._dataset), desc='Checking', leave=False):
            if not self.func(item):
                bad_items.append(i)

        if len(bad_items):
            raise DataValidationException(f'Items {bad_items} are not valid')
        else:
            print('OK!')
