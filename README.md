![header](docs/imgs/header.png)
ML Engineering framework with the aim to standardize the work with data and models, make experiments more reproducible,
ML development more fast.  
The general idea is to make abstract `Dataset` and `Model` classes with very basic interfaces 
(much like pytorch base classes Dataset and Module, but with different meaning) 
and then use them to build more specific tools.  
This project is an attempt to build such bundle of tools for ML-Engineer, certain standards and guides for 
workflow, a set of templates for typical tasks.

## Basic structure
Cascade is divided into three main modules namely: `data`, `models` and `meta`  
- `data` aims to provide OOP-solution to the problem of building complex data-pipelines
- `models` provides standardized way of dealing with ML-models, train, evaluate, save, load, etc...
- `meta` ensures that all relevant meta info about data and models is stored

![footer](docs/imgs/footer.png)
