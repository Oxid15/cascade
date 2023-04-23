![header](cascade/docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)
[![Downloads](https://pepy.tech/badge/cascade-ml)](https://pepy.tech/project/cascade-ml)

Flexible ML Engineering library with the aim to standardize the work with data and models, make experiments more reproducible, ML development faster.  

Cascade built for individuals or small teams that are in need of ML Engineering solution, but don't have time or resources to use large enterprise-level systems.  

**Included in [Model Lifecycle](https://github.com/kelvins/awesome-mlops#model-lifecycle) section of Awesome MLOps list**

## Installation

```bash
pip install cascade-ml
```

More info on installation can be found in [documentation](https://oxid15.github.io/cascade/quickstart.html#installation)

## Documentation

[Go to Cascade documentation](https://oxid15.github.io/cascade/)

## Usage

This section is divided into blocks based on what problem you can solve using Cascade. These are the simplest examples
of what the library is capable of. See more in documentation.

### ETL pipeline tracking

Data processing pipelines need to be versioned and tracked as a part of model experiments.  
To track changes and version everything about data Cascade has Datasets - special wrappers
that encapsulate changes that are done during preprocessing.

```python
from cascade import data as cdd

from sklearn.datasets import load_digits
import numpy as np


# Load dataset
X, y = load_digits(return_X_y=True)
pairs = [(x, y) for (x, y) in zip(X, y)]

# To track all preparation stages we wrap cdd.Dataset over
# collection of items and targets
ds = cdd.Wrapper(pairs)

# Let's make a pipeline - shuffle the dataset
ds = cdd.RandomSampler(ds)

# Splitting the data is also tracked in pipeline's metadata
train_ds, test_ds = cdd.split(ds)

# Add small noise to images
train_ds = cdd.ApplyModifier(
    train_ds,
    lambda pair: pair + np.random.random() * 0.1 - 0.05
)

# Let's see the metadata we got
from pprint import pprint

pprint(train_ds.get_meta())
```

We see all the stages that we did in meta.

```json
[{"len": 898,
  "name": "cascade.data.apply_modifier.ApplyModifier",
  "type": "dataset"},
 {"len": 898,
  "name": "cascade.data.range_sampler.RangeSampler",
  "type": "dataset"},
 {"len": 1797,
  "name": "cascade.data.random_sampler.RandomSampler",
  "type": "dataset"},
 {"len": 1797,
  "name": "cascade.data.dataset.Wrapper",
  "obj_type": "<class 'list'>",
  "type": "dataset"}]
```

However, the pipelines are changing frequently and these changes during experiments are rarely got version-tracked.
Cascade has a solution for this.

```python
# We save the dataset's meta into the version log
# if something will change in the pipeline
# the version will be updated

cdd.VersionAssigner(train_ds, 'version_log.yml')
```

See all datasets in [zoo](https://oxid15.github.io/cascade/examples/dataset_zoo.html)  
See all use-cases in [documentation](https://oxid15.github.io/cascade/quickstart.html)

### Experiment tracking

Not only data and pipelines changes over time. Models change more frequently and require special system to handle experiments and artifacts.

```python
from cascade import models as cdm
from cascade import data as cdd

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Define the simple model that using
# basic methods from cdm.BasicModel
class BaselineModel(cdm.BasicModel):
    def __init__(self, const=0, *args, **kwargs) -> None:
        self.const = const
        super().__init__(const=const, *args, **kwargs)

    def predict(self, x, *args, **kwargs):
        return [self.const for _ in range(len(x))]

    # Models define the way whey are trained loaded and saved
    # we don't use these here, but they exist
    def fit(self, *args, **kwargs):
        pass

    def save(self, path):
        pass


model = BaselineModel(1)

# Fit and evaluate do not return anything
model.fit(X_train, y_train)
model.evaluate(X_test, y_test, {'acc': accuracy_score, 'f1': f1_score})

# Model repository is the solution for experiment and artifact storage
repo = cdm.ModelRepo('repos/use_case_repo')

# Repo is the collection of model lines
# Line can be a bunch of experiments on one model type
line = repo.add_line('baseline')

# We save the model - everything is held automatically
line.save(model, only_meta=True)

from pprint import pprint
pprint(model.get_meta())
```

Let's see what is saved as meta data of this experiment.

```json
[
    {
        "name": "<__main__.BaselineModel object at 0x000001F69F493820>",
        "created_at": "2023-01-02T16:36:59.041979+00:00",
        "metrics": {
            "acc": 0.6293706293706294,
            "f1": 0.7725321888412017
        },
        "params": {
            "const": 1
        },
        "type": "model",
        "saved_at": "2023-01-02T16:36:59.103781+00:00"
    }
]
```

See all use-cases in [documentation](https://oxid15.github.io/cascade/quickstart.html)

### Data validation

Validation is an important part of pipelines. Simple asserts can do the thing, but
there is more useful validation tools.  
Validators provide meaningful error messages and a way to perform many checks in one run over the dataset.

```python
from cascade import meta as cme
from cascade import data as cdd

from sklearn.datasets import load_digits
import numpy as np


# Load data
X, y = load_digits(return_X_y=True)
pairs = [(x, y) for (x, y) in zip(X, y)]

# Let's define a pipeline
ds = cdd.Wrapper(pairs)
ds = cdd.RandomSampler(ds)
train_ds, test_ds = cdd.split(ds)

# Validate using this tool
cme.PredicateValidator(
    train_ds,
    [
        lambda pair: all(pair[0] < 20),
        lambda pair: pair[1] in (i for i in range(10))
    ]
)

```

See all use-cases in [documentation](https://oxid15.github.io/cascade/quickstart.html)

### Metadata analysis

During experiments Cascade produces many metadata which can be analyzed later.
`MetricViewer` is the tool that allows to see the relationship between parameters and
metrics of all models in repository.

```python
from cascade import meta as cme
from cascade import models as cdm

# Open the existing repo
repo = cdm.ModelRepo('repos/use_case_repo')

# This runs web-server that relies on optional dependency
cme.MetricViewer(repo).serve()
```

![metric-viewer](cascade/docs/imgs/metric-viewer.gif)

`HistoryViewer` allows to see model's lineage, what parameters resulted in what metrics

```python
from cascade import meta as cme
from cascade import models as cdm


repo = cdm.ModelRepo('repos/use_case_repo')

# This returns plotly figure
cme.HistoryViewer(repo).plot()

# This runs a server ans allows to see changes in real time (for example while models are trained)
cme.HistoryViewer(repo).serve()

```

See all use-cases in [documentation](https://oxid15.github.io/cascade/quickstart.html)

![history-viewer](cascade/docs/imgs/history-viewer.gif)

## Who could find Cascade useful

Small and fast-prototyping AI-teams could use it as a tradeoff between total missingness of any ML-Engineering framework and demanding enterprise solutions.

## Principles

The key principles of Cascade are:

* **Elegancy** - ML code should be about ML with minimum meta-code
* **Flexibility** - to easily build prototypes and integrate existing projects with Cascade *(don't pay for what you don't use)*
* **Reusability** - code to be reused in similar projects with no effort
* **Traceability** - everything should have meta-data

## Contributing

Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests and docs as appropriate.

## License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)

## Versions

This project uses Semantic Versioning - <https://semver.org/>

![footer](cascade/docs/imgs/footer.png)
