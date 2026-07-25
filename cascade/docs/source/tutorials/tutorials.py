# %%
# Pipelines basics

from sklearn.datasets import load_digits

# %%
from cascade.data import Dataset


class DigitsDataset(Dataset):
    def __init__(self) -> None:
        self.x, self.y = load_digits(return_X_y=True)
        super().__init__()

    def get(self, index):
        item = {
            "x": self.x[index],
            "y": self.y[index],
        }
        return item

    def __len__(self):
        return len(self.x)


# %%
ds = DigitsDataset()
print(ds[0])

# %%
import numpy as np

from cascade.data import ApplyModifier

NOISE_RANGE = (-1, 1)


def add_noise(item):
    item["x"] = item["x"] + np.random.randint(*NOISE_RANGE)
    return item


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

from sklearn.linear_model import LogisticRegression

# %%
from cascade.models import BasicModel


class LR(BasicModel):
    def __init__(self, penalty):
        self.model = LogisticRegression(penalty=penalty)
        super().__init__()

    def fit(self, dataset):
        x, y = [], []
        for item in dataset:
            x.append(item["x"])
            y.append(item["y"])

        self.model.fit(x, y)

    def predict(self, x):
        return self.model.predict(x)


# %%
model = LR("l2")
model.fit(ds)

# %%
model.params["penalty"] = "l2"

# %%
from cascade.lines import ModelLine

line = ModelLine("line", model_cls=LR)
line.save(model)

# %%

model = line.load(0)
x = [item["x"] for item in ds]
preds = model.predict(x)

print(preds[0], ds[0]["y"])

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
        "noise_range": NOISE_RANGE,
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
print(version)  # 0.2

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
# Metrics and evaluation

# %%
from sklearn.metrics import f1_score


def f1(gt, pred):
    return f1_score(gt, pred, average="macro")


x = [item["x"] for item in loaded_ds]
y = [item["y"] for item in loaded_ds]

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
# Meta defaults
# %%

model.describe("This is simple linear model")

# %%

model.tag(["tutorial", "dummy"])

# %%

model.link(ds)
model.link(name="training_file", uri=__file__)

# %%

pprint(model.get_meta())

# %%

model.remove_tag("dummy")

# %%

model.remove_link("1")

# %%

pprint(model.get_meta())
line.save(model)

# %%
from pydantic import BaseModel


class LabeledImage(BaseModel):
    x: np.ndarray
    y: int

    model_config = {"arbitrary_types_allowed": True}


# %%
from cascade.data import SchemaModifier


class ValidatingModifier(SchemaModifier):
    in_schema = LabeledImage

    def get(self, idx):
        item = self._dataset[idx]
        # Here you can do anything
        return item


# %%

ds = ValidatingModifier(ds)


# %%

print(ds[0])

# %%


class EvilDataset(Dataset):
    def get(self, idx):
        return {"x": np.zeros(18 * 18), "y": "hehe"}

    def __len__(self):
        return 67


# %%

from cascade.data import ValidationError

evil = EvilDataset()
evil = ValidatingModifier(evil)

try:
    evil[0]
except ValidationError as e:
    print(e)


# %%

import os
import pickle

from sklearn.neural_network import MLPClassifier


class NeuralNet(BasicModel):
    def __init__(self):
        self._model = MLPClassifier()
        super().__init__()

    def save_artifact(self, path: str) -> None:
        with open(os.path.join(path, "artifact.pkl"), "wb") as f:
            pickle.dump(self._model, f)

    def load_artifact(self, path: str) -> None:
        with open(os.path.join(path, "artifact.pkl"), "rb") as f:
            self._model = pickle.load(f)


# %%

nn = NeuralNet()
line.save(nn)

# %%
last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
print(os.listdir(last_model_dir))
print(os.listdir(os.path.join(last_model_dir, "artifacts")))

# %%
import json

dummy_predictions = [0, 1, 2, 3]

with open("dummy_predictions.json", "w") as f:
    json.dump(dummy_predictions, f)

# %%

nn.add_file("dummy_predictions.json")
line.save(nn)

# %%

last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
print(os.listdir(last_model_dir))
print(os.listdir(os.path.join(last_model_dir, "files")))

# %%

from cascade.utils.sklearn import SkModel

model = SkModel(blocks=[LogisticRegression()])

# %%

ds = DigitsDataset()

x = [item["x"] for item in ds]
y = [item["y"] for item in ds]

model.fit(x, y)

# %%

from cascade.utils.sklearn import SkMetric

model.evaluate(
    x,
    y,
    [
        SkMetric("f1_score", average="macro"),
        SkMetric("acc"),
    ],
)

# %%

pprint(model.metrics)

line.save(model)

# %%

last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
print(os.listdir(last_model_dir))

# %%
