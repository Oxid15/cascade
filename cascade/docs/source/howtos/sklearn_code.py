# %%
from cascade.utils.sklearn import SkModel
from sklearn.feature_selection import SelectKBest
from sklearn.svm import SVC

# %%
k_best = 2

model = SkModel(
    blocks=[
        SelectKBest(k=k_best),
        SVC(),
    ],
    k=k_best,
)

# %%
from sklearn.datasets import load_iris

iris = load_iris()
model.fit(iris.data, iris.target)

# %%

model.predict([iris.data[0]]), iris.target[0]

# %%
from cascade.utils.sklearn import SkMetric

metrics = [
    SkMetric("acc"),
    SkMetric("f1", average="macro"),
    SkMetric("precision_score", average="macro"),
    SkMetric("recall_score", average="macro"),
]

# %%

metrics.append(
    SkMetric()
)

# %%

model.evaluate(iris.data, iris.target, metrics=metrics)

# %%
from pprint import pprint

pprint(model.metrics)
# %%
# [SkMetric(name=acc, value=0.9533333333333334, created_at=2024-09-16 19:06:05.354980+00:00),
#  SkMetric(name=f1, value=0.9532912954992826, created_at=2024-09-16 19:06:05.355031+00:00),
#  SkMetric(name=precision_score, value=0.9543690619563763, created_at=2024-09-16 19:06:05.355048+00:00),
#  SkMetric(name=recall_score, value=0.9533333333333333, created_at=2024-09-16 19:06:05.355060+00:00)]

# %%

from cascade.lines import ModelLine

line = ModelLine("sklearn_demo", model_cls=SkModel)
line.save(model)
