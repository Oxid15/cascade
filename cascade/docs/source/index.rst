Small-scale MLOps library
#########################

Cascade is MLOps for projects that don't need a MLOps platform.

Track experiments, datasets, models and artifacts locally with Python and your filesystem. No tracking server, cloud account or complex infrastructure required.


.. meta::
   :description: Open-source Python MLOps library for lightweight experiment tracking. Configuration management, ML pipeline building and data validation tools for small-scale development.
   :keywords: cascade, mlops, small-scale mlops, local experiment tracking, pipelines, data validation

.. code-block:: bash

    pip install cascade-ml

No need for a platform
**********************

What you get without tracking server, cloud or complex setup

* Local UI
* Experiment tracking
* Configuration management
* Data lineage and validation
* Experiment results querying


Local UI
********

.. code-block:: bash

    pip install cascade-ui

Just do ``cascade ui`` to get a nice dashboard for your experiments

.. image:: _static/cascade_ui_screens.gif
  :alt: UI demo of Cascade - Small scale MLOps library

See more docs on :ref:`/tutorials/ui.rst`

Experiment tracking
*******************

.. grid:: 1

    .. grid-item::
        .. card:: :octicon:`repo` Track what parameters influcenced your metrics
            :link: tutorials/tutorials.html#experiments-basics

            Effortless parameter and metric tracking

    .. grid-item::
        .. card:: :octicon:`file-binary` Store everything locally
            :link: tutorials/tutorials.html#artifacts-and-files

            Structured artifact storage without the need for cloud

    .. grid-item::
        .. card:: :octicon:`telescope` Query results
            :link: tutorials/results_querying.html

            Use CLI to access your experiments

Configuration management
************************

.. grid:: 1

    .. grid-item::
        .. card:: :octicon:`terminal` Experiment quickly without boilerplate
            :link: tutorials/configuration_management.rst

            Run experiments from terminal without writing code for flags or reading configs

    .. grid-item::
        .. card:: :octicon:`terminal` CLI
            :link: tutorials/tutorials.html#cli

            Comment, tag and write experiment descriptions from command line


Dataset versioning
******************

.. grid:: 1

    .. grid-item::
        .. card:: :octicon:`stack` Know the lineage of your training data
            :link: tutorials/tutorials.html#pipelines-basics

            Traceable data transformations from modular blocks

    .. grid-item::
        .. card:: :octicon:`codescan-checkmark` Train only with clean data
            :link: tutorials/tutorials.html#data-validation

            Data validation tools

Comparison with other MLOps tools
*********************************

Cascade is designed for local-first ML development and small teams. Here is how it compares to other popular MLOps tools.

.. list-table::
   :header-rows: 1
   :widths: 18 18 18 18 18 18
   :align: center

   * - Feature
     - Cascade
     - Aim
     - MLflow
     - W&B
     - ClearML
   * - Local-first
     - **Yes**
     - **Yes**
     - Partial
     - No
     - No
   * - Configuration management
     - **Yes**
     - No
     - No
     - **Yes**
     - No
   * - Data lineage
     - **Yes**
     - No
     - Partial
     - Partial
     - **Yes**
   * - Data validation
     - **Yes**
     - No
     - Partial
     - No
     - No
   * - Experiment results querying
     - **Yes** 
     - **Yes**
     - **Yes**
     - **Yes**
     - **Yes**
   * - Local Web UI
     - **Yes**
     - **Yes**
     - **Yes**
     - No
     - No
   * - Target scale
     - **Individuals → small teams**
     - **Individuals → small teams**
     - Small teams → Enterprise scale
     - Larger teams → Enterprise scale
     - Larger teams → Enterprise scale
   * - Setup complexity
     - **Low**
     - **Low**
     - Medium
     - Hard
     - Hard


Quickstart
**********

Here is a simple example of how you can use
Cascade to track an ``sklearn`` classifier.

0. Install Cascade
==================

.. code-block:: bash

    pip install cascade-ml

1. Track an experiment
======================

You can integrate Cascade into an existing project without making many changes.
Everything is tracked and stored locally using the filesystem you can manage.

.. code-block:: python

    import random
    from sklearn.linear_model import LogisticRegression
    from cascade.lines import ModelLine
    from cascade.utils.sklearn import SkModel

    model = SkModel(
        blocks = [
            LogisticRegression()
        ]
    )
    model.tag("training")
    model.describe("Regression model for index page demo")
    model.add_metric('acc', random.random())

    line = ModelLine("index_demo_line")
    line.save(model)

2. Get rich metadata
====================

You can find information about the model you have tracked in ``index_demo_line/00000/meta.json``

.. code-block:: python

    [
        {
            "name": "cascade.utils.sklearn.sk_model.SkModel",
            "description": "Regression model for index page demo",
            "tags": [
                "training"
            ],
            "comments": [],
            "links": [],
            "type": "model",
            "created_at": "2026-09-04T13:54:28.273927+00:00",
            "metrics": [
                {
                    "name": "acc",
                    "value": 0.20003771067823384,
                    "created_at": "2026-09-04T13:58:28.868433+00:00"
                }
            ],
            "params": {},
            "pipeline": "Pipeline(steps=[('0', LogisticRegression())])",
            "path": "/home/ilia/work/cascade/line/00000",
            "slug": "dramatic_gibbon_of_swiftness",
            "saved_at": "2026-09-04T13:59:05.717339+00:00",
            "python_version": "3.12.3 (main, Mar 23 2026, 19:04:32) [GCC 13.3.0]",
            "user": "ilia",
            "host": "your-pc-name",
            "cwd": "/home/ilia/cascade",
            "git_commit": "ddcb2f700d64592c3e433209dff5c6c5d544906f",
            "git_uncommitted_changes": [
                "M cascade/docs/source/index.rst\n?? line/"
            ]
        }
    ]


Documentation
*************

.. grid:: 2

    .. grid-item::
        .. card:: :octicon:`mortar-board` Tutorial
            :link: /tutorials/tutorials.rst
            :link-type: ref

            Learn how you can use Cascade in your ML workflows step-by-step

    .. grid-item::
        .. card:: :octicon:`tasklist` How-to guides
            :link: /howtos/howtos.rst
            :link-type: ref

            Recipes for specific use-cases

    .. grid-item::
        .. card:: :octicon:`book` Explanations
            :link: /explanations/explanations.rst
            :link-type: ref

            Theoretical basis of Cascade

    .. grid-item::
        .. card:: :octicon:`bookmark` Reference
            :link: /modules/modules.rst
            :link-type: ref

            Cascade API Reference

Key Principles
**************
* Elegance - ML code should be about ML with minimum meta-code
* Agility - it should be easy to build prototypes and integrate existing project with Cascade
* Reusability - code should have an ability to be reused in similar projects
* Traceability - everything should have meta data


If you have any questions
*************************

Any contributions are welcome!

:octicon:`pencil` `Write an issue <https://github.com/Oxid15/cascade/issues>`_

:octicon:`flame` `Join GitHub discussions <https://github.com/Oxid15/cascade/discussions>`_

:octicon:`megaphone` `Cascade on X <https://x.com/cascade_mlops>`_

.. toctree::
    :maxdepth: 1
    :hidden:

    tutorials/tutorials
    howtos/howtos
    explanations/explanations
    modules/modules
