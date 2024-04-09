Welcome to Cascade!
###################

Lightweight and modular MLOps library with the aim to make ML development more efficient targeted at small teams or individuals.

Who could find it useful
************************
The slope of adopting MLOps platforms can sometimes be too steep for individuals.
However, they can still benefit from some MLOps practices integrated into the workflow.
Cascade offers the solution that enables those features for small projects while demanding little.
In small-scale ML-projects there is usually no need for the whole MLOps setups (at least in early stages).
Taking this in mind, Cascade is built modular to enable users to fit the solution to their specific needs
by using different parts of the library without the need to bring everything at once.

Key Principles
**************
* Elegancy - ML code should be about ML with minimum meta-code
* Agility - it should be easy to build prototypes and integrate existing project with Cascade
* Reusability - code should have an ability to be reused in similar projects
* Traceability - everything should have meta data

Introduction
************
Cascade does not require complex setups. To start use it you just need to install the python package.

Installation
------------

.. code-block:: bash

    pip install cascade-ml

More info on installation and first steps can be found in :ref:`/quickstart.rst` page.

Experiment tracking
-------------------
Cascade is built to be modular and flexible so that integration of Cascade
in your existing workflow could become gradual.

The simplest case is the experiment tracking - store your models structured
along with all meta data.

.. code-block:: python

    from cascade.models import BasicModel, ModelRepo
    import random

    # Your existing experiment can remain unchanged

    model = BasicModel()
    model.params.update({"learning_rate": 1e-10})

    model.link(name="dataset", uri="../data/dataset")
    model.add_metric("f1", random.random()) # Your metric value
    model.add_file("example_plot.png")

    repo = ModelRepo("classification")
    line = repo.add_line("resnet")
    line.save(model)

This brief example shows that you can easily start experiment tracking
from your current setup.

Cascade allows you to abstract from structuring your experiment results and model artifacts storage.
It creates and manages repositories of models from which they can be extracted easily
for evaluation or deployment.

.. code-block:: 

    |- classification
    |  |- resnet
    |  |  |- 00000
    |  |  |  |- artifacts
    |  |  |  |- files

What is saved as default meta data in ``classification/resnet/00000/meta.json``

.. code-block:: json

    [
        {
            "comments": [],
            "created_at": "2023-09-18T19:43:48.146504+00:00",
            "description": null,
            "links": ["name": "dataset", "uri": "../data/dataset", "meta": null],
            "metrics": [{"created_at": "2023-09-18T19:44:39.853785+00:00",
                        "dataset": null,
                        "direction": null,
                        "interval": null,
                        "name": "f1",
                        "split": null,
                        "value": 0.45756550190760725}],
            "name": "cascade.models.model.Model",
            "params": {"learning_rate": 1e-10},
            "path": "/home/ilia/classification/resnet/00000",
            "saved_at": "2023-09-18T19:46:00.099433+00:00",
            "slug": "perky_awesome_coua",
            "tags": [],
            "type": "model"
        }
    ]

Meta data is a very flexible structure and you can save and modify whatever
information you want.

For more advanced usage of ``Model`` see :ref:`/examples/model_training.ipynb` page

Build pipelines
---------------

The amount of work that is put in the building data processing pipelines is
proportional to the role clean and well prepared data plays in the final
performance of ML solution.

This is where Datasets come in. Consider this toy-example where the data would be
a sequence of digits.

Cascade offers a library of useful default datasets and modifiers along with
a modular paradigm of independent pipeline steps as modifiers.

.. code-block:: python

    from cascade import data as cdd


    ds = cdd.Wrapper([0, 1, 2, 3, 4])
    ds = cdd.ApplyModifier(ds, lambda x: x**2)

In this example our data goes through three stages that are defined above.
The pipeline is defined in a declarative way and each step will be executed as the
particular item requested.

Though the main feature of datasets is their metadata.
To get metadata of an object you do just:

.. code-block:: python

    train_ds.get_meta()

.. code-block:: json

    [
        {
            "comments": [],
            "description": null,
            "len": 5,
            "links": [],
            "name": "cascade.data.apply_modifier.ApplyModifier",
            "tags": [],
            "type": "dataset"
        },
        {
            "comments": [],
            "description": null,
            "len": 5,
            "links": [],
            "name": "cascade.data.dataset.Wrapper",
            "obj_type": "<class 'list'>",
            "tags": [],
            "type": "dataset"
        }
    ]

By default all `sized` objects will have length in their meta data.

All datasets with examples can be found in :ref:`/examples/dataset_zoo.ipynb`

.. toctree::
    :maxdepth: 1
    :hidden:

    quickstart
    examples
    modules
