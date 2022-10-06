from math import floor
from typing import Tuple
from . import Dataset, RangeSampler


def split(ds: Dataset, frac=0.5, num=None) -> Tuple[Dataset]:
    '''
    Splits dataset into two cascade.data.RangeSampler`s

    Parameters
    ----------
    frac: float
        A fraction for division of dataset.
        For example if frac=0.8, then first dataset gets 80% of items and the second gets 20%.
        Is not used, when `num` is specified.
    num: int
        A number of items that first dataset will get. The second one will get len(dataset) - num items.

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
    '''
    if num is None:
        num = floor(len(ds) * frac)

    return RangeSampler(ds, 0, num), RangeSampler(ds, num, len(ds))
