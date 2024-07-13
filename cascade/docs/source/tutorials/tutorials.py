# %%
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
    return np.clip(x[0] + np.random.randint(-1, 1), 0, 15), x[1]


ds_noise = ApplyModifier(ds, add_noise)

print(ds_noise[0])

# %%
from cascade.data import Concatenator

ds = Concatenator([ds, ds_noise])
print(len(ds))

# %%
from cascade.models import BasicModel
from sklearn.linear_model import LogisticRegression


class LR(BasicModel):
    def __init__(self):
        self.model = LogisticRegression()
        super().__init__()

    def fit(self, dataset):
        x, y = [], []
        for item in dataset:
            x.append(item[0])
            y.append(item[1])
        self.model.fit(x, y)

    def predict(self, dataset):
        return self.model.predict([item[0] for item in dataset])

# %%
model = LR()
model.fit(ds)

# %%
from cascade.lines import ModelLine

line = ModelLine("line", model_cls=BasicModel)
line.save(model)

# %%

model = line.load(0)
y = model.predict(ds)

print(y[0], ds[0][1])
