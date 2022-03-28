from tqdm import tqdm
from . import Modifier, Wrapper, T


class BruteforceCacher(Modifier):
    def __init__(self, dataset):
        super(BruteforceCacher, self).__init__(dataset)
        self._data = [item for item in tqdm(self._dataset)] # forcibly calling all previous lazy loads

    def __getitem__(self, index) -> T:
        return self._data[index]
