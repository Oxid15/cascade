from . import Sampler, T


class CyclicSampler(Sampler):
    """
    A Sampler that iterates `num_samples` times through an input Dataset in cyclic manner

    Example:
    --------
    >>> from cascade.data import CyclicSampler
    >>> from cascade.tests.number_dataset import NumberDataset
    >>> ds = NumberDataset([1,2,3])
    >>> ds = CyclicSampler(ds, 5)
    >>> for item in ds:
    ...     print(item)
    ...
    1
    2
    3
    1
    2
    """
    def __getitem__(self, index) -> T:
        internal_index = index % len(self._dataset)
        return self._dataset[internal_index]
