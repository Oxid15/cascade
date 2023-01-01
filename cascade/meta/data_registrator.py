import os
from ..base import MetaHandler
from ..data import Dataset, T


class DataRegistrator:
    def __init__(self, path: str) -> None:
        self._path = path
        self._mh = MetaHandler()

        if os.path.exists(path):
            try:
                self._meta = self._mh.read(path)
            except IOError as e:
                raise IOError(f'Failed to read log file: {path}') from e
        else:
            self._meta = {}

    def register(self, ds: Dataset[T]):
        pass
