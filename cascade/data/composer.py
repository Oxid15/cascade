from typing import List, Iterable, Tuple, Dict
from . import T, Dataset


class Composer(Dataset):
    """
    Unifies two or more datasets element-wise.

    Example
    -------
    >>> from cascade import data as cdd
    >>> items = cdd.Wrapper([0, 1, 2, 3, 4])
    >>> labels = cdd.Wrapper([1, 0, 0, 1, 1])
    >>> ds = cdd.Composer((items, labels))
    >>> assert ds[0] == (0, 1)
    """
    def __init__(self, datasets: Iterable[Dataset], *args, **kwargs) -> None:
        """
        Parameters
        ----------
        datasets: Iterable[Dataset]
            Datasets of the same length to be unified
        """
        super().__init__(*args, **kwargs)
        self._validate_input(datasets)
        self._datasets = datasets
        # Since we checked the same length in all datasets, we can
        # set the length of any dataset as the length of Composer
        self._len = len(self._datasets[0])

    def _validate_input(self, datasets):
        lengths = [len(ds) for ds in datasets]
        first = lengths[0]
        if not all([ln == first for ln in lengths]):
            raise ValueError(
                f'The datasets passed should be of the same length\n'
                f'Actual lengths: {lengths}'
            )

    def __getitem__(self, index: int) -> Tuple[T]:
        return tuple(ds[index] for ds in self._datasets)

    def __len__(self) -> int:
        return self._len

    def get_meta(self) -> List[Dict]:
        """
        Composer calls `get_meta()` of all its datasets
        """
        meta = super().get_meta()
        meta[0]['data'] = [ds.get_meta() for ds in self._datasets]
        return meta
