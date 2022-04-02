import numpy as np
from .dataset import Dataset, T


class Concatenator(Dataset):
    def __init__(self, datasets) -> None:
        self._datasets = datasets
        lengths = [len(ds) for ds in self._datasets]
        self.shifts = np.cumsum([0] + lengths)

    def __getitem__(self, index) -> T:
        ds_index = 0
        for sh in self.shifts[1:]:
            if index >= sh:
                ds_index += 1
        return self._datasets[ds_index][index - self.shifts[ds_index]]

    def __len__(self) -> int:
        return sum([len(ds) for ds in self._datasets])

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp} of\n' + '\n'.join(repr(ds) for ds in self._datasets)

    def get_meta(self) -> dict:
        meta = super().get_meta()
        for ds in self._datasets:
            meta += ds.get_meta()
        return meta
