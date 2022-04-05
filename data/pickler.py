import os
import pickle
from . import Modifier


class Pickler(Modifier):
    """
    Pickles an input dataset or unpickles one
    """
    def __init__(self, path, dataset=None) -> None:
        """
        Loads pickled dataset or dumps one depending on parameters passed

        If only path is passed - loads dataset from path provided if path exists
        if path provided with a dataset dumps dataset to the path

        Parameters:
        -----------
        path:
            path to the pickled dataset
        dataset: Dataset, optional
            a dataset to be pickled
        """
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
