import os
import pickle
from . import Modifier


class Pickler(Modifier):
    def __init__(self, path, dataset=None) -> None:
        super().__init__(dataset)
        self.path = path

        if self._dataset is None:
            assert os.path.exists(self.path)
            self._load()
        else:
            self._dump()

    def _dump(self) -> None:
        with open(self.path, 'wb') as f:
            pickle.dump(self._dataset, f)

    def _load(self) -> None:
        with open(self.path, 'rb') as f:
            self._dataset = pickle.load(f)
