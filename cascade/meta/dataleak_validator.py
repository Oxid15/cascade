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

from typing import Any, Callable, Optional

from tqdm import tqdm

from ..data.dataset import BaseDataset, T
from .validator import DataValidationException, Validator, prettify_items


class DataleakValidator(Validator):
    def __init__(
        self,
        train_ds: BaseDataset[T],
        test_ds: BaseDataset[T],
        hash_fn: Optional[Callable[[Any], str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Checks if two datasets have identical items

        Calculates ``hash_fn`` to identify items
        Uses python ``hash`` as default, but can be customized

        Parameters
        ----------
        train_ds : Dataset[T]
            Train dataset
        test_ds : Dataset[T]
            Test or evaluation dataset
        hash_fn : Optional[Callable[[Any], str]]
            Hash function, by default None

        Raises
        ------
        DataValidationException
            If identical items found

        Example
        -------
        >>> from cascade.meta import DataleakValidator
        >>> from cascade.data import Wrapper
        >>> import numpy as np
        >>> train_ds = Wrapper(np.zeros((5, 2)))
        >>> test_ds = Wrapper(np.zeros((5, 2)))
        >>> from cascade.meta import DataleakValidator, numpy_md5
        >>> DataleakValidator(train_ds, test_ds, hash_fn=numpy_md5)
        Traceback (most recent call last):
        ...
        cascade.meta.validator.DataValidationException:
        Train and test datasets have 25 repeating pairs
        Train indices: 0, 0, 0, 0, 0 ... 4, 4, 4, 4, 4
        Test indices: 0, 1, 2, 3, 4 ... 0, 1, 2, 3, 4
        """
        if hash_fn is None:
            hash_fn = hash

        train_hashes = [
            hash_fn(item) for item in tqdm(train_ds, desc="Retrieve train data")
        ]
        test_hashes = [
            hash_fn(item) for item in tqdm(test_ds, desc="Retrieve test data")
        ]

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
                f"Train and test datasets have {size} repeating pairs\n"
                f"Train indices: {prettify_items(train_repeating_idx)}\n"
                f"Test indices: {prettify_items(test_repeating_idx)}"
            )
        else:
            print("OK!")

        super().__init__(self, train_ds, **kwargs)
