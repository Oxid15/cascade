Quickstart
==========

Installation
------------
Install latest version using pip directly from main branch

.. code-block:: bash

    pip install cascade-ml

.. note::
    Requirements of `cascade.utils` are optional and listed in the file `utils_requirements.txt`
    Since 0.11.0 all submodules of utils made separate which means you are not longer in need to install all these 
    dependencies at once to use some submodule.


Demo
----
The following demo is built to showcase what you can do using Cascade.
This is one example that tries to include every aspect of functionality and serve as a 
guide for building workflows with Cascade.

Requirements
~~~~~~~~~~~~
This example will use latest cascade and sklearn which you can install using
.. code-block:: bash

    pip install scikit-learn==1.4.1

Dataset
~~~~~~~

Cascade features data pipeline building tools that
allow constructing data processing procedures from
reusable blocks and also manage metadata of those
procedures to record what blocks were used with what parameters
in each experiment.

In this example Cascade wrapper around sklearn wine
dataset is created. It defines two required
methods which are `__len__` and `__getitem__`.
In addition it adds number of features to
`get_meta` method which will add this info
into metadata of the dataset.

.. code-block:: python

    from cascade import data as cdd
    from sklearn.datasets import load_wine


    class WineDataset(cdd.Dataset):
        def __init__(self, *args, **kwargs):
            self.x, self.y = load_wine(return_X_y=True)
            super().__init__(*args, **kwargs)

        def __getitem__(self, i: int):
            return self.x[i], self.y[i]

        def __len__(self):
            return len(self.y)

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["n_features"] = self.x.shape[0]
            return meta


    ds = WineDataset()
    ds = cdd.RandomSampler(ds)
    train_ds, test_ds = cdd.split(ds, frac=0.8)

Read More
^^^^^^^^^
:ref:`/examples/dataset.rst`

Model
~~~~~

Like datasets, models in Cascade wrap underlying contents
into a standard reusable interface with the ability to track
metadata.

In some cases wrappers are already implemented and reside in the
`utils` module - for all the functionality that requires a dependency
that is too-specific to include in the general package.

In this case `sklearn` model wrapper is used.

.. code-block:: python

    from cascade.utils.sklearn import SkModel
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC

    models = [
        SkModel(blocks=[SVC()]),
        SkModel(blocks=[LogisticRegression()])
    ]

    x, y = [item[0] for item in train_ds], [item[1] for item in train_ds]
    for model in models:
        model.fit(x, y)

Read More
^^^^^^^^^
:ref:`/examples/model.rst`
:ref:`/examples/model_training.ipynb`
:ref:`/examples/model_training_trainers.ipynb`

Metric
~~~~~~

Metrics are very important part of ML workflow and Cascade treats
them specially. As models, metrics standardize the interface and
in addition offer an extensive set of default fields that should
satisfy most of the cases.

In Cascade metrics define the way they are computed, store their value
and also manage their metadata. More on that can be read in `this post about
metrics implementation on Cascade <https://oxid15.github.io/posts/en/2024/03/02/reimplementation-of-metrics-in-cascade.html>`.

In this example wrapper is implemented for F1-score metric.
Although for sklearn-based metrics Cascade has already created wrappers
this is made for demonstrational purposes.

.. code-block:: python

    from cascade.metrics import Metric
    from sklearn.metrics import f1_score


    class F1(Metric):
        def __init__(self, average, dataset, split) -> None:
            self.average = average
            extra = {"average": average}
            super().__init__(name="F1", dataset=dataset, split=split, direction="up", extra=extra)

        def compute(self, gt, pred):
            self.value = f1_score(gt, pred, average=self.average)
            return

Here is how evaluation process works. Since models and metrics all share
standard interfaces the evaluation process becomes very simple.

For each model we record two metrics and metric in turn store dataset and split.

.. code-block:: python

    from cascade.utils.sklearn import SkMetric

    x, y = [item[0] for item in test_ds], [item[1] for item in test_ds]
    for model in models:
        model.evaluate(x, y, metrics=[
            F1(average="macro", dataset="wine", split="test"),
            SkMetric("acc", dataset="wine", split="test")
        ])
        print(model.metrics)

Repos and Lines
---------------

Repos and Lines are Cascade's metadata storage units.

.. code-block:: python

    from cascade.models import ModelRepo

    repo = ModelRepo("./demo")
    svc_line = repo.add_line("svc")
    lr_line = repo.add_line("lr")
    lines = [svc_line, lr_line]

    for model, line in zip(models, lines):
        model.link(train_ds)
        model.link(test_ds)

        line.save(model)

