from uuid import uuid1
import numpy as np
from .dataset import Dataset


class Concatenator(Dataset):
    def __init__(self, datasets):
        self._datasets = datasets
        lengths = [len(ds) for ds in self._datasets]
        self.shifts = np.cumsum([0] + lengths)

    def __getitem__(self, index):
        ds_index = 0
        for sh in self.shifts[1:]:
            if index >= sh:
                ds_index += 1
        return self._datasets[ds_index][index - self.shifts[ds_index]]

    def __len__(self):
        return sum([len(ds) for ds in self._datasets])

    def __repr__(self):
        rp = super().__repr__()
        return f'{rp} of {", ".join(ds.__repr__() for ds in self._datasets)}'

    def get_meta(self) -> dict:
        meta = {str(uuid1()): self.__repr__()}
        meta_others = {str(uuid1()): ds.get_meta() for ds in self._datasets}
        meta.update(meta_others)
        return meta
