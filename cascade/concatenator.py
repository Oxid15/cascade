import numpy as np
from .dataset import Dataset


class Concatenator(Dataset):
    def __init__(self, datasets):
        self.datasets = datasets
        lengths = [len(ds) for ds in self.datasets]
        self.shifts = np.cumsum([0] + lengths)

    def __getitem__(self, index):
        ds_index = 0
        for sh in self.shifts[1:]:
            if index >= sh:
                ds_index += 1
        return self.datasets[ds_index][index - self.shifts[ds_index]]

    def __len__(self):
        return sum([len(ds) for ds in self.datasets])
