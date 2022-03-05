# Cascade
ML Engineering framework with the aim to standardize the work with data and models, make it object-oriented.  
The general idea is to give abstract Dataset and Model classes (much like pytorch base classes Dataset and Module, but more high-level) and then use them to build more specific tools.
  
For example general workflow with datasets could look like this:
```python
from cascade.data import Dataset


# We have some very basic abstract dataset
# and customize it for some specific purpose
class NumberDataset(Dataset):
    def __init__(self, data):
        self._data = data


# Then we need to perform some preprocess and
# we implement it with another dataset now as a modifier
class MultiplyModifier(Dataset):
    def __getitem__(self, index):
        return self._data[index] * 2


ds = NumberDataset([1, 2, 3, 4, 5])
ds = MultiplyModifier(ds)
```
This enables object-oriented solution. 
The operations on dataset can be lazy as 
in example above or can be implemented in
__init__ to force whole data update

Calls in this system are made cascade-like - hence the name of the project.

