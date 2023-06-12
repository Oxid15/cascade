Welcome to Cascade!
###################

ML Engineering library with the aim to standardize the work with data and models, make experiments more reproducible, ML development more fast.
  
This project is an attempt to build a bundle of tools for ML-Engineer, certain standards and guides for 
workflow, a set of templates for typical tasks.

Who could find it useful
************************
Small and fast-prototyping ML-teams and especially single ML developers
could use it as a tradeoff between total absence of any MLOps 
framework and demanding enterprise solutions.

Key Principles
**************
* Elegancy - ML-pipelines code should be about ML with minimum meta-code
* Agility - it should be easy to build new prototypes and integrate existing project with Cascade
* Reusability - code should have an ability to be reused in similar projects with little or no effort
* Traceability - everything should have meta data

Introduction
************
Cascade is built for small teams and individuals and does not require any
complex setups. To start use it you just need to install the python package.

Installation
------------

.. code-block:: bash

    pip install cascade-ml

More info on installation can be found in :ref:`/quickstart.rst` page.

Track your first experiment
---------------------------
Integration of Cascade in your existing workflow can be at different levels.
The simplest case is the experiment tracking - store your models structured
along with all meta data.

.. code-block:: python3

    from cascade.models import Model, ModelRepo
    import random


    model = Model()
    model.params.update({'learning_rate': 1e-10})

    # Your existing experiment here

    model.metrics.update({'f1': random.random()})

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
            "name": "<cascade.models.model.Model object at 0x7f4fb0391270>",
            "created_at": "2023-06-12T09:49:56.741950+00:00",
            "metrics": {
                "f1": 0.4956132247067879
            },
            "params": {
                "learning_rate": 1e-10
            },
            "type": "model",
            "saved_at": "2023-06-12T09:55:15.865675+00:00"
        }
    ]

Meta data is a very flexible structure and you can save and modify whatever
information you want.

For more advanced usage of ``Model`` see :ref:`/examples/model_training.ipynb` page

.. toctree::
    :titlesonly:
    :maxdepth: 1

    quickstart
    concepts
    modules
