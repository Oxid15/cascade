from math import floor
from . import Dataset, RangeSampler


def split(ds: Dataset, frac=0.5, num=None):
    if num is None:
        num = floor(len(ds) * frac)

    return RangeSampler(ds, 0, num), RangeSampler(ds, num, len(ds))
