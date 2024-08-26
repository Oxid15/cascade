Tutorial
========

Tutorial is a set of lessons that will teach you
basics of Cascade. Lessons are connected in a single project
and depend on each other.
You can grasp the essence of how
you can use the library for your own projects, while
completing this one.

Installation
------------

Install the latest version using pip

.. code-block:: bash

    pip install cascade-ml

Cascade has a set of optional dependencies, which can be installed with the following commands

.. code-block:: bash

    pip install cascade-ml[opencv] # Use opencv as image backend
    pip install cascade-ml[pandera] # Validate pandas dataframes with Pandera
    pip install cascade-ml[pil] # Use Pillow as image backend
    pip install cascade-ml[pydantic] # Use data validation modifiers
    pip install cascade-ml[sklearn] # Scikit-learn integration
    pip install cascade-ml[torch] # PyTorch integration
    pip install cascade-ml[view] # Cascade viewers based on dash
    pip install cascade-ml[all] # Installs everything

If you have completed the tutorial you can see the :ref:`/howtos/howtos.rst` section
for more specific and complex workflows.

.. toctree::
    :maxdepth: 1

    pipelines_basics
    metadata
    experiments_basics
    custom_meta_and_versioning
    metrics_and_evaluation
    meta_defaults
    repos_and_workspaces
    cli
    viewers
    data_validation
    artifacts
    sklearn
    next
