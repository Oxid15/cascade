![header](cascade/docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)
[![Downloads](https://pepy.tech/badge/cascade-ml)](https://pepy.tech/project/cascade-ml)

Flexible ML Engineering library with the aim to standardize the work with data and models, make experiments more reproducible, ML development faster.  

Cascade built for individuals or small teams that are in need of ML Engineering solution, but don't have time or resources to use large enterprise-level systems.  

The main principle is that you should't pay for what you don't use.



# Installation

```bash
pip install cascade-ml
```
More info on installation can be found in [documentation](https://oxid15.github.io/cascade/quickstart.html#installation)



# Documentation

---
[Go to Cascade documentation](https://oxid15.github.io/cascade/)



# Usage
This section is divided into blocks based on what problem you can solve using Cascade.

## ETL pipeline tracking
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



# Contributing

Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests and docs as appropriate.



# License

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) 



# Versions

This project uses Semantic Versioning - https://semver.org/


![footer](cascade/docs/imgs/footer.png)
