![header](docs/imgs/header.png)

![ver](https://img.shields.io/github/v/release/oxid15/cascade?style=plastic)
![build](https://github.com/oxid15/cascade/actions/workflows/python-package.yml/badge.svg)

ML Engineering framework with the aim to standardize the work with data and models, make experiments more reproducible,
ML development more fast.  
The general idea is to make abstract `Dataset` and `Model` classes with very basic interfaces 
(much like pytorch base classes Dataset and Module, but with different meaning) 
and then use them to build more specific tools.  
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


class SpecificImageDataset(FolderDataset):
    def __getitem__(self, index):
        name = self.names[index]
        img = cv2.imread(name)
        return img


class PreprocessModifier(Modifier):
    def __getitem__(self, index):
        img = super().__getitem__(index)
        img = torch.Tensor(img)
        return img


ds = SpecificImageDataset('./images')
ds = PreprocessModifier(ds)

dl = DataLoader(ds)

# Train your model
        
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests and docs as appropriate.

## Documentation
Docs are available online: [cascade docs](https://oxid15.github.io/cascade/)

## License
[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/) 


## Basic structure

Cascade is divided into three main modules namely: `data`, `models` and `meta`  

- `data` aims to provide OOP-solution to the problem of building complex data-pipelines
- `models` provides standardized way of dealing with ML-models, train, evaluate, save, load, etc...
- `meta` ensures that all relevant meta info about data and models is stored anbd can be easily viewed

There is also `utils` which is a collection of useful Datasets and Models, but are too specific to add them to the core.

## Versions

This project uses Semantic Versioning - https://semver.org/

![footer](docs/imgs/footer.png)

