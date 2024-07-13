#%%
from cascade.data import Dataset
from sklearn.datasets import load_digits


class DigitsDataset(Dataset):
    def __init__(self) -> None:
        self.x, self.y = load_digits(return_X_y=True)
        super().__init__()

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return len(self.x)

# %%
ds = DigitsDataset()
print(ds[0])

# %%
import numpy as np
from cascade.data import ApplyModifier


def add_noise(x):
    return np.clip(x[0] + np.random.randint(-2, 2), 0, 15), x[1]


ds_noise = ApplyModifier(ds, add_noise)

print(ds_noise[0])

# %%
from cascade.data import Concatenator

ds = Concatenator([ds, ds_noise])
print(len(ds))
