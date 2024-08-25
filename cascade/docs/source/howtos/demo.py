# pip install scikit-learn==1.4.1

# %%

from sklearn.datasets import load_wine

from cascade import data as cdd


class WineDataset(cdd.Dataset):
    def __init__(self, *args, **kwargs):
        self.x, self.y = load_wine(return_X_y=True)
        super().__init__(*args, **kwargs)

    def __getitem__(self, i: int):
        return self.x[i], self.y[i]

    def __len__(self):
        return len(self.y)

    def get_meta(self):
        meta = super().get_meta()
        meta[0]["n_features"] = self.x.shape[0]
        return meta


ds = WineDataset()
ds = cdd.RandomSampler(ds)
train_ds, test_ds = cdd.split(ds, frac=0.8)

# %%

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from cascade.utils.sklearn import SkModel

models = [SkModel(blocks=[SVC()]), SkModel(blocks=[LogisticRegression()])]

x, y = [item[0] for item in train_ds], [item[1] for item in train_ds]
for model in models:
    model.fit(x, y)

# %%

from sklearn.metrics import f1_score

from cascade.metrics import Metric


class F1(Metric):
    def __init__(self, average, dataset, split) -> None:
        self.average = average
        extra = {"average": average}
        super().__init__(
            name="F1", dataset=dataset, split=split, direction="up", extra=extra
        )

    def compute(self, gt, pred):
        self.value = f1_score(gt, pred, average=self.average)
        return self.value


# %%

from cascade.utils.sklearn import SkMetric

x, y = [item[0] for item in test_ds], [item[1] for item in test_ds]
for model in models:
    model.evaluate(
        x,
        y,
        metrics=[
            F1(average="macro", dataset="wine", split="test"),
            SkMetric("acc", dataset="wine", split="test"),
        ],
    )
    print(model.metrics)

# %%

from cascade.models import ModelRepo

repo = ModelRepo("./demo")
svc_line = repo.add_line("svc")
lr_line = repo.add_line("lr")
lines = [svc_line, lr_line]

for model, line in zip(models, lines):
    model.link(train_ds)
    model.link(test_ds)

    line.save(model)

# %%

from cascade.meta import MetricViewer

mv = MetricViewer(repo)
mv.table[mv.table["name"] == "F1"]
best_model = mv.table[mv.table["name"] == "F1"].sort_values("value").iloc[0].to_dict()
print(best_model)
