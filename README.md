![header](docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)

Small ML Engineering framework with the aim to standardize the work with data and models, make experiments more reproducible, ML development more fast.  
  
This project is an attempt to build such bundle of tools for ML-Engineer, certain standards and guides for 
workflow, a set of templates for typical tasks.

## Installation

Install latest version from main branch
```bash
python -m pip install git+https://github.com/oxid15/cascade.git@main
```

## Usage
The simplest use-case is pipeline building.

```python
import torch
from torch.utils.data import DataLoader
import cv2

from cascade.data import Modifier, FolderDataset

# Define Dataset - an entity responsible for fetching data from source
class SpecificImageDataset(FolderDataset):
    # Since everything is held in FolderDataset and Dataset classes
    # we need to only define __geiitem__
    def __getitem__(self, index):
        name = self.names[index]
        img = cv2.imread(name)
        return img


class PreprocessModifier(Modifier):
    # Same with Modifier - only __getitem__
    def __getitem__(self, index):
        img = super().__getitem__(index)
        img = torch.Tensor(img)
        return img


ds = SpecificImageDataset('./images')
ds = PreprocessModifier(ds)

# Pass images further to train your model
``` 
## Why Cascade

Cascade emerged as an attempt to bring order into messy and fast-paced ML-engineering workflow.  
As a part of small AI-team I encountered *typical problems* for those who run a lot of fast experiments on datasets and models with no strict system, which are:
 * Growing number of different versions of data pipeline
 * Growing number of different versions of models
 * Folders with hundreds of models as binary artifacts with no info about what is inside
 * History of model's metrics is not present
 * Data pipelines and model trainloops are difficult to reuse
 * New data coming to the training stage passes without verification 

### This project aims to address this kind of issues by:
 * Making data pipelines modular, traceable and verifiable with little or no additional code
 * Making models more than black-box binary artifacts
 * Introducing tools for storing and accessing meta data, parameters and metrics

## Why not other solutions
For ML-Engineering teams there are a number of tools available, which are:
 * [mlflow](https://mlflow.org/)
 * [DVC](https://dvc.org/)
 * [neptune.ai](https://neptune.ai/)
 * [zenml](https://github.com/zenml-io/zenml)
  
These are great tools for their own purposes, however with their own weaknesses
 * A lot of imperative meta-code
 * The need to restructure your pipelines to fit in the system
 * No support for tracing data-pipelines
 * No focus on what is inside data processing scripts, only on MLOps meta-code
 * Difficult to manage quick experiments, prototypes

## Who could find Cascade useful
Small and fast-prototyping AI-teams could use it as a tradeoff between total missingness of any ML-Engineering framework and demanding enterprise solutions.

## Principles
The key principles of Cascade are:
 * **Elegancy** - ML-pipelines code should be about ML with minimum meta-code
 * **Agility** - it should be easy to build new prototypes and wrap old ones into framework
 * **Reusability** - code should have an ability to be reused in similar projects with little or no effort
 * **Traceability** - everything should have meta-data

The logo of the project is a depiction of these principles: it symbolizes modularity, standartization, information flow and is cascade-like :)

## Contributing
Pull requests and issues are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests and docs as appropriate.

## Documentation
Docs are available online:  
[Go to Cascade documentation](https://oxid15.github.io/cascade/)

Cascade is divided into three main modules namely: `data`, `models` and `meta`  

- `data` aims to provide OOP-solution to the problem of building complex data-pipelines
- `models` provides standardized way of dealing with ML-models, train, evaluate, save, load, etc...
- `meta` ensures that all relevant meta info about data and models is stored anbd can be easily viewed

There is also `utils` which is a collection of useful Datasets and Models which are too specific to add them to the core.

## License
[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) 

## Versions

This project uses Semantic Versioning - https://semver.org/

![footer](docs/imgs/footer.png)
