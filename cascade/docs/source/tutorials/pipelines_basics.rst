Pipelines basics
================
In this tutorial you will learn basic pipeline building blocks of Cascade.
This is the first Cascade tutorial from a series. All of the tutorials are
meant to form one big project and can be thought of as a series of lessons.

Each lesson will come with a list of links for further reading or advanced
how-to guides on related topics.

Cascade pipelines allow building data processing routines from interchangeable
steps called `Datasets` and `Modifiers`.

Datasets are the sources of data. In the first step let's make a Dataset
for `digits` from `sklearn`.

.. code-block:: python

    from cascade.data import Dataset
    from sklearn.datasets import load_digits


    class DigitsDataset(Dataset):
        def __init__(self) -> None:
            self.x, self.y = load_digits(return_X_y=True)
            super().__init__()

        def __getitem__(self, index):
            return self.x[index], self.y[index]

        def __len__(self):
            return len(self.x)

Minimal setup for a Dataset is a `__getitem__` and `__len__` methods.
Now we can do basic access.

.. code-block:: python

    ds = DigitsDataset()
    print(ds[0])

Cascade Datasets are not only a system of data organization. They
allow using rich set of defaults for data manipulation.

.. code-block:: python

    import numpy as np
    from cascade.data import ApplyModifier


    def add_noise(x):
        return np.clip(x[0] + np.random.randint(-2, 2), 0, 15), x[1]


    ds_noise = ApplyModifier(ds, add_noise)

    print(ds_noise[0])

`Modifiers` take datasets and transform their values.
In previous example we added noise to digits by using `ApplyModifier`
and created new noisy dataset.

We can augment our data by concatenating those two datasets.

.. code-block:: python

    from cascade.data import Concatenator

    ds = Concatenator([ds, ds_noise])
    print(len(ds))
