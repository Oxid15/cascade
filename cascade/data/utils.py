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

from math import floor
from typing import Optional, Tuple, Union

from .dataset import Dataset, IteratorDataset, T
from .range_sampler import RangeSampler

DatasetOrIterator = Union[Dataset[T], IteratorDataset[T]]


def split(
    ds: Dataset[T], frac: Optional[float] = 0.5, num: Optional[int] = None
) -> Tuple[RangeSampler[T], RangeSampler[T]]:
    """
    Splits dataset into two cascade.data.RangeSampler

    Parameters
    ----------
    frac: float
        A fraction for division of dataset.
        For example if frac=0.8, then first dataset gets 80% of items and the second gets 20%.
        Is not used, when ``num`` is specified.
    num: int
        A number of items that first dataset will get.
        The second one will get len(dataset) - num items.

    Example
    -------
    >>> ds = cdd.Wrapper([0, 1, 2, 3, 4])

    >>> ds1, ds2 = cdd.split(ds)
    >>> print([item for item in ds1])
    [0, 1]

    >>> print([item for item in ds2])
    [2, 3, 4]

    >>> ds1, ds2 = cdd.split(ds, 0.6)

    >>> print([item for item in ds1])
    [0, 1, 2]
    >>> print([item for item in ds2])
    [3, 4]

    >>> ds1, ds2 = cdd.split(ds, num=4)

    >>> print([item for item in ds1])
    [0, 1, 2, 3]
    >>> print([item for item in ds2])
    [4]
    """
    if num is None and frac is None:
        raise ValueError("Either num or frac must be specified. Got both None")

    if num is None:
        num = floor(len(ds) * frac)

    return RangeSampler(ds, 0, num), RangeSampler(ds, num, len(ds))
