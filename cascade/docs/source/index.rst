Welcome to Cascade!
###################

Lightweight and modular MLOps library with the aim to make ML development more efficient targeted at small teams or individuals.

Who could find it useful
************************
The slope of adopting MLOps platforms can sometimes be too steep for small teams.
However, they can still benefit from MLOps practices integrated into the workflow.
Cascade offers the solution that enables those features for small projects while demanding little.

Key Principles
**************
* Elegancy - ML code should be about ML with minimum meta-code
* Agility - it should be easy to build prototypes and integrate existing project with Cascade
* Reusability - code should have an ability to be reused in similar projects
* Traceability - everything should have meta data

Introduction
************
Cascade does not require any complex setups. To start use it you just need to install the python package.

Installation
------------

.. code-block:: bash

    pip install cascade-ml

More info on installation can be found in :ref:`/quickstart.rst` page.

Track your first experiment
---------------------------
Cascade is built to be modular and flexible so that integration of Cascade
in your existing workflow could become gradual.

The simplest case is the experiment tracking - store your models structured
along with all meta data.

.. code-block:: python

    from cascade.models import Model, ModelRepo
    import random


    model = Model()
    model.params.update({'learning_rate': 1e-10})

    # Your existing experiment here

    model.add_metric('f1', random.random())

    repo = ModelRepo('classification')
    line = repo.add_line('resnet')
    line.save(model, only_meta=True)

This brief example shows that you can easily start experiment tracking
from your current setup.
Cascade allows you to abstract from structuring your model storage. Note
that in this example ``only_meta`` is stored. We haven't define ``save()``
method of our model and cannot save it. Let's see what is saved.

.. code-block:: 

    |- classification         # Repo folder
    |  |- resnet              # Line folder
    |  |  |- 00000            # Model folder
    |  |  |  |- meta.json
    |  |  |- meta.json
    |  |- meta.json

What is saved as default meta data in ``classification/resnet/00000/meta.json``

.. code-block:: json

    [
        {
            "comments": [],
            "created_at": "2023-09-18T19:43:48.146504+00:00",
            "description": null,
            "links": [],
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

The amount of work we put in the building data processing pipelines is
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
            'comments': [],
            'description': None,
            'len': 5,
            'links': [],
            'name': 'cascade.data.apply_modifier.ApplyModifier',
            'tags': [],
            'type': 'dataset'
        },
        {
            'comments': [],
            'description': None,
            'len': 5,
            'links': [],
            'name': 'cascade.data.dataset.Wrapper',
            'obj_type': "<class 'list'>",
            'tags': [],
            'type': 'dataset'
        }
    ]

By default all `sized` objects will have length in their meta data.
The more specific the transformation the richer meta will be.

All datasets with examples can be found in :ref:`/examples/dataset_zoo.ipynb`

.. toctree::
    :maxdepth: 1
    :hidden:

    quickstart
    examples
    concepts
    modules
