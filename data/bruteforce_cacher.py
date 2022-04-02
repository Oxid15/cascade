from tqdm import tqdm, trange
from . import Modifier, Wrapper, T


class BruteforceCacher(Modifier):
    def __init__(self, dataset) -> None:
        super(BruteforceCacher, self).__init__(dataset)
        # forcibly calling all previous datasets in the init
        if hasattr(self._dataset, '__len__'):
            self._data = [self._dataset[i] for i in trange(len(self._dataset))]
        elif hasattr(self._dataset, '__next__'):
            self._data = [item for item in self._dataset]
        else:
            raise AttributeError(f'Input dataset must provide Listlike or Iterable interface')

    def __getitem__(self, index) -> T:
        return self._data[index]
