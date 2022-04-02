import os
import sys

sys.path.append(os.path.abspath('../..'))
from cascade.data import Dataset


class NumberDataset(Dataset):
    def __init__(self, arr):
        self.numbers = arr

    def __getitem__(self, index):
        return self.numbers[index]

    def __len__(self):
        return len(self.numbers)