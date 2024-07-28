# %%
# Pipelines basics

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

NOISE_MAGNITUDE = 1


def add_noise(x):
    return np.clip(x[0] + np.random.randint(-NOISE_MAGNITUDE, NOISE_MAGNITUDE), 0, 15), x[1]


ds_noise = ApplyModifier(ds, add_noise)

print(ds_noise[0])

# %%
from cascade.data import Concatenator

ds = Concatenator([ds, ds_noise])
print(len(ds))

# %%
# Experiment basics

# %%
from pprint import pprint

pprint(ds.get_meta())

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

    def predict(self, x):
        return self.model.predict(x)


# %%
model = LR()
model.fit(ds)

# %%
from cascade.lines import ModelLine

line = ModelLine("line", model_cls=BasicModel)
line.save(model)

# %%

model = line.load(0)
x = [item[0] for item in ds]
preds = model.predict(x)

print(preds[0], ds[0][1])

# %%
from pprint import pprint

pprint(line.load_model_meta(0))

# %%
# Custom Meta and Versioning

# %%
from cascade.lines import DataLine

ds.update_meta(
    {
        "long_description": "This is digits pipeline. It was augmented with some uniform noise",
        "noise_magnitude": NOISE_MAGNITUDE,
    }
)

# %%

dataline = DataLine("dataline")
dataline.save(ds)

# %%

version = dataline.get_version(ds)
print(version)

# %%

ds.update_meta({"detail_i_almost_forgot": "Changes in meta bump minor version"})
version = dataline.get_version(ds)
print(version) # 0.2

dataline.save(ds)

# %%

changed_ds = ApplyModifier(ds, add_noise)
dataline.save(changed_ds)
version = dataline.get_version(changed_ds)
print(version)

# %%
version = dataline.get_version(ds)
print(version)

loaded_ds = dataline.load("0.2")
version = dataline.get_version(loaded_ds)
print(version)

# %%
from sklearn.metrics import f1_score


def f1(gt, pred):
    return f1_score(gt, pred, average="macro")


x = [item[0] for item in loaded_ds]
y = [item[1] for item in loaded_ds]

model.evaluate(x, y, [f1])

pprint(model.metrics)

# %%
from cascade.metrics import Metric


class Accuracy(Metric):
    def __init__(self):
        super().__init__(name="acc")

    def compute(self, gt, pred):
        self.value = sum([g == p for g, p in zip(gt, pred)]) / len(gt)
        return self.value


model.evaluate(x, y, [Accuracy()])

pprint(model.metrics)

# %%
line.save(model)

pprint(line.load_model_meta(1))

# %%

model.describe("This is simple linear model")

# %%

model.tag("tutorial")

# %%

model.link(ds)
model.link(name="training_file", uri=__file__)

pprint(model.get_meta())

line.save(model)

# %%

from cascade.meta import MetricViewer

mv = MetricViewer(line)

print(mv.table.head())
