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

from typing import Callable, Union, Any
from tqdm import tqdm

from . import Validator, DataValidationException
from .validator import prettify_items
from ..data import Dataset, T


class DataleakValidator(Validator):
    def __init__(
            self,
            train_ds: Dataset[T],
            test_ds: Dataset[T],
            hash_fn: Union[Callable[[Any], str], None] = None,
            **kwargs: Any
    ) -> None:
        if hash_fn is None:
            hash_fn = hash

        train_hashes = [hash_fn(item) for item in tqdm(train_ds, desc='Retrieve train data')]
        test_hashes = [hash_fn(item) for item in tqdm(test_ds, desc='Retrieve test data')]

        train_repeating_idx = []
        test_repeating_idx = []
        for i, train_hash in enumerate(train_hashes):
            for j, test_hash in enumerate(test_hashes):
                if train_hash == test_hash:
                    train_repeating_idx.append(i)
                    test_repeating_idx.append(j)

        size = len(train_repeating_idx)
        if size > 0:
            raise DataValidationException(
                f'Train and test datasets have {size} common items\n'
                f'Train indices: {prettify_items(train_repeating_idx)}\n'
                f'Test indices: {prettify_items(test_repeating_idx)}'
            )
        else:
            print('OK!')

        super().__init__(self, train_ds, **kwargs)
