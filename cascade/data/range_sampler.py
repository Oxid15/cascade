from . import T, Dataset, Sampler


class RangeSampler(Sampler):
    """
    Implements an interface of standard range in a dataset.

    Example
    -------
    >>> from cascade.data import RangeSampler, Wrapper
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> # Define start, stop and step exactly as in range()
    >>> sampler = RangeSampler(ds, 1, 5, 2) 
    >>> for item in sampler:
    ...     print(item)
    ...
    2
    4
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> sampler = RangeSampler(ds, 3)
    >>> for item in sampler:
    ...     print(item)
    ...
    1
    2
    3
    """
    def __init__(self, dataset: Dataset, start=None, stop=None, step=1, *args, **kwargs) -> None:
        if start is not None and stop is None:
            stop = start
            start = 0

        self._indices = [i for i in range(start, stop, step)]
        super().__init__(dataset, len(self._indices), *args, **kwargs)

    def __getitem__(self, index) -> T:
        internal_index = self._indices[index]
        return super().__getitem__(internal_index)
