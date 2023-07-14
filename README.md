![header](cascade/docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)
[![Downloads](https://pepy.tech/badge/cascade-ml)](https://pepy.tech/project/cascade-ml)
[![DOI](https://zenodo.org/badge/460920693.svg)](https://zenodo.org/badge/latestdoi/460920693)

Flexible ML Engineering library with the aim to standardize the work with data and models, make experiments more reproducible, ML development faster.  

Cascade built for individuals or small teams that are in need of ML Engineering solution, but don't have time or resources to use large enterprise-level systems.  

**Included in [Model Lifecycle](https://github.com/kelvins/awesome-mlops#model-lifecycle) section of Awesome MLOps list**

## Installation

```bash
pip install cascade-ml
```

More info on installation can be found in [documentation](https://oxid15.github.io/cascade/en/latest/quickstart.html#installation)

## Documentation

[Go to Cascade documentation](https://oxid15.github.io/cascade/en/latest)

## Usage

This section is divided into blocks based on what problem you can solve using Cascade. These are the simplest examples
of what the library is capable of. See more in documentation.

### ETL pipeline tracking

Data processing pipelines need to be versioned and tracked as a part of model experiments.  
To track changes and version everything about data Cascade has Datasets - special wrappers
that encapsulate changes that are done during preprocessing.

```python
from pprint import pprint
from cascade import data as cdd
from sklearn.datasets import load_digits
import numpy as np


X, y = load_digits(return_X_y=True)
pairs = [(x, y) for (x, y) in zip(X, y)]

# To track all preparation stages we wrap cdd.Dataset
ds = cdd.Wrapper(pairs)

# This creates pipeline
ds = cdd.RandomSampler(ds)
train_ds, test_ds = cdd.split(ds)
train_ds = cdd.ApplyModifier(
    train_ds,
    lambda pair: pair + np.random.random() * 0.1 - 0.05
)

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

See all datasets in [zoo](https://oxid15.github.io/cascade/en/latest/examples/dataset_zoo.html)  
See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)

### Experiment tracking

Not only data and pipelines changes over time. Models change more frequently and require special system to handle experiments and artifacts.

```python
import random
from cascade import models as cdm
from cascade import data as cdd

model = cdm.Model()
model.metrics.update({
    'acc': random.random()
})

# Repo is the collection of model lines
repo = cdm.ModelRepo('repos/use_case_repo')

# Line can be a bunch of experiments on one model type
line = repo.add_line('baseline')
line.save(model, only_meta=True)
```

Let's see what is saved as meta data of this experiment.

```json
[
    {
        "name": "cascade.models.model.Model",
        "created_at": "2023-05-29T21:06:23.341752+00:00",
        "metrics": {
            "acc": 0.6745652975946803
        },
        "params": {},
        "type": "model",
        "saved_at": "2023-05-29T21:06:25.977728+00:00"
    }
]
```

See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)

### Data validation

Validation is an important part of pipelines. Simple asserts can do the thing, but
there is more useful validation tools.  
Validators provide meaningful error messages and a way to perform many checks in one run over the dataset.

```python
from cascade import meta as cme
from cascade import data as cdd

from sklearn.datasets import load_digits
import numpy as np


X, y = load_digits(return_X_y=True)
pairs = [(x, y) for (x, y) in zip(X, y)]

ds = cdd.Wrapper(pairs)
ds = cdd.RandomSampler(ds)
train_ds, test_ds = cdd.split(ds)

cme.PredicateValidator(
    train_ds,
    [
        lambda pair: all(pair[0] < 20),
        lambda pair: pair[1] in (i for i in range(10))
    ]
)
```

See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)

### Metadata analysis

During experiments Cascade produces many metadata which can be analyzed later.
`MetricViewer` is the tool that allows to see the relationship between parameters and
metrics of all models in repository.

```python
from cascade import meta as cme
from cascade import models as cdm

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

See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)

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

## Cite the code

If you used the code in your research, please cite it with:  
  
[![DOI](https://zenodo.org/badge/460920693.svg)](https://zenodo.org/badge/latestdoi/460920693)

```bibtex
@software{ilia_moiseev_2023_8006995,
  author       = {Ilia Moiseev},
  title        = {Oxid15/cascade: Lightweight ML Engineering library},
  month        = jun,
  year         = 2023,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.8006995},
  url          = {https://doi.org/10.5281/zenodo.8006995}
}
```

![footer](cascade/docs/imgs/footer.png)
