from typing import Callable
from . import Dataset, Modifier, T


class ApplyModifier(Modifier):
    """
    Modifier that maps a function to previous dataset's elements in a lazy way.
    """
    def __init__(self, dataset: Dataset, func: Callable) -> None:
        """
        Parameters:
        -----------
        dataset: Dataset
            a dataset to modify
        func: Callable
            a function to be applied to every item of a dataset -
            each `__getitem__` would call `func` on an item obtained from a previous dataset
        """
        super().__init__(dataset)
        self.func = func

    def __getitem__(self, index: int) -> T:
        item = self._dataset[index]
        return self.func(item)

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp}, {repr(self.func)}'
