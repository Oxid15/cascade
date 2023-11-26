![header](cascade/docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)
[![Downloads](https://pepy.tech/badge/cascade-ml)](https://pepy.tech/project/cascade-ml)
[![DOI](https://zenodo.org/badge/460920693.svg)](https://zenodo.org/badge/latestdoi/460920693)

Lightweight and modular MLOps library with the aim to make ML development more efficient targeted at small teams or individuals.

Cascade was built especially for individuals or small teams that are in need of MLOps, but don't have time or resources to integrate with platforms.

**Included in [Model Lifecycle](https://github.com/kelvins/awesome-mlops#model-lifecycle) section of Awesome MLOps list**

## Installation

```bash
pip install cascade-ml
```

More info on installation can be found in [documentation](https://oxid15.github.io/cascade/en/latest/quickstart.html#installation)

## Docs

[Go to Cascade documentation](https://oxid15.github.io/cascade/en/latest)

## Usage

This section is divided into blocks based on what problem you can solve using Cascade. These are the simplest examples
of what the library is capable of. See more in documentation.

### ETL pipeline tracking

Data processing pipelines need to be versioned and tracked as a part of model experiments.  
To track changes and version everything about data Cascade has `Datasets` - special wrappers
that encapsulate operations on data.

```python
from pprint import pprint
from cascade import data as cdd
from sklearn.datasets import load_digits
import numpy as np


X, y = load_digits(return_X_y=True)
pairs = [(x, y) for (x, y) in zip(X, y)]

ds = cdd.Wrapper(pairs)
ds = cdd.RandomSampler(ds)

train_ds, test_ds = cdd.split(ds)
train_ds = cdd.ApplyModifier(
    train_ds,
    lambda pair: pair + np.random.random() * 0.1 - 0.05
)

pprint(train_ds.get_meta())
```

We see all the stages that we did in meta.

<details>
<summary>Click to see full pipeline metadata</summary>

```json
[{"comments": [],
  "description": null,
  "len": 898,
  "links": [],
  "name": "cascade.data.apply_modifier.ApplyModifier",
  "tags": [],
  "type": "dataset"},
 {"comments": [],
  "description": null,
  "len": 898,
  "links": [],
  "name": "cascade.data.range_sampler.RangeSampler",
  "tags": [],
  "type": "dataset"},
 {"comments": [],
  "description": null,
  "len": 1797,
  "links": [],
  "name": "cascade.data.random_sampler.RandomSampler",
  "tags": [],
  "type": "dataset"},
 {"comments": [],
  "len": 1797,
  "links": [],
  "name": "cascade.data.dataset.Wrapper",
  "obj_type": "<class 'list'>",
  "tags": [],
  "type": "dataset"}]
```

</details>

See all datasets in [zoo](https://oxid15.github.io/cascade/en/latest/examples/dataset_zoo.html)  
See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)


### Pipeline versioning

Cascade offers automatic pipeline versioning
utilities

```python
from cascade.data import Wrapper, Modifier, version

ds = Wrapper([0, 1, 2])
ds = Modifier(ds)

ver = version(ds, "version_log.yml")
```

Will output `0.1` and for any change in the steps or any meta of the pipeline it will
bump the version. If you return to the previous version, then will return to previous one as well.

### Experiment tracking

Not only data and pipelines changes over time. Models change more frequently and require special system to handle experiments and artifacts.

```python
import random
from cascade import models as cdm
from cascade import data as cdd

model = cdm.Model()
model.add_metric('acc', random.random())

repo = cdm.ModelRepo('repos/use_case_repo')

line = repo.add_line('baseline')
line.save(model, only_meta=True)
```

`Repo` is the collection of model lines and `Line` can be a bunch of experiments on one model type.


<details>
<summary>Click to see full model metadata</summary>

```json
[{"comments": [],
  "created_at": "2023-11-06T07:42:42.737248+00:00",
  "description": null,
  "links": [],
  "metrics": [{"created_at": "2023-11-06T07:42:43.004261+00:00",
               "name": "acc",
               "value": 0.3730907820891789}],
  "name": "cascade.models.model.Model",
  "params": {},
  "path": "/home/user/repos/use_case_repo/baseline/00001",
  "saved_at": "2023-11-06T07:43:17.325593+00:00",
  "slug": "cerulean_jaguarundi_of_trust",
  "tags": [],
  "type": "model"}]
```

</details>


See all use-cases in [documentation](https://oxid15.github.io/cascade/en/latest/examples.html)

### Data validation

Validation is an important part of pipelines. Simple asserts can do the thing, but
there are more useful validation tools.  
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

Small and fast-prototyping AI-teams could use it as a tradeoff between total missingness of any MLOps practices and demanding enterprise solutions.

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
