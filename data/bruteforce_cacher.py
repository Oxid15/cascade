from tqdm import tqdm, trange
from . import Dataset, Modifier, T


class BruteforceCacher(Modifier):
    """
    Unusual modifier which loads everything in memory in initialization phase
    and then returns values from cache
    """
    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        # forcibly calling all previous datasets in the init
        if hasattr(self._dataset, '__len__') and hasattr(self._dataset, '__getitem__'):
            self._data = [self._dataset[i] for i in trange(len(self._dataset))]
        elif hasattr(self._dataset, '__iter__'):
            self._data = [item for item in tqdm(self._dataset)]
        else:
            raise AttributeError('Input dataset must provide Mapping or Iterable interface')

    def __getitem__(self, index) -> T:
        return self._data[index]

    def __len__(self):
        return len(self._data)
