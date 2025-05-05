Cascade - small-scale MLOps library with experiment tracking
############################################################

Lightweight and modular MLOps library with the aim to make ML development more efficient targeted at small teams or individuals.

.. meta::
   :description: Open-source MLOps library for lightweight experiment tracking. Configuration management, ML pipeline building and data validation tools for small-scale development.
   :keywords: cascade, mlops, ml, experiment tracking, pipelines, data validation

.. code-block:: bash

    pip install cascade-ml

Who could find it useful
************************
The slope of adopting MLOps platforms can sometimes be too steep for small-scale teams.
However, they can still benefit from some MLOps practices integrated into the workflow.

MLOps for everyone
******************

Cascade offers the solution that enables these features for small projects while demanding little.
There is usually no need for the full MLOps setups in most of the small-scale ML-projects.
Taking this in mind, Cascade is built modular to enable users to tailor the solution to their specific needs
by using different parts of the library without the need to bring everything at once.

.. grid:: 2

    .. grid-item::
        .. card:: :octicon:`stack` Pipeline building
            :link: tutorials/tutorials.html#pipelines-basics

            Build traceable data transformations from modular blocks

    .. grid-item::
        .. card:: :octicon:`repo` Experiment management
            :link: tutorials/tutorials.html#experiments-basics

            Write your parameters and metrics in a structured way

    .. grid-item::
        .. card:: :octicon:`file-binary` Artifact and file storage
            :link: tutorials/tutorials.html#artifacts-and-files

            Store your models and files locally

    .. grid-item::
        .. card:: :octicon:`codescan-checkmark` Data validation
            :link: tutorials/tutorials.html#data-validation

            Be sure that your data is clean

Advanced features
*****************

.. grid:: 2

    .. grid-item::
        .. card:: :octicon:`terminal` CLI
            :link: tutorials/tutorials.html#cli

            Comment, tag and write experiment descriptions from command line

    .. grid-item::
        .. card:: :octicon:`telescope` Query results
            :link: tutorials/results_querying.html

            Use CLI to access your experiments (if you have too many of them)

    .. grid-item::
        .. card:: :octicon:`graph` Dash-based visualizations
            :link: tutorials/tutorials.html#viewers

            See plots and tables in dash-based web interface

    .. grid-item::
        .. card:: :octicon:`zap` Web-UI

            :bdg-info:`Coming soon!`


Experiment management
*********************

Here is a simple example of how you can use
Cascade to track an ``sklearn`` classifier.

1. Define a Model
=================

.. code-block:: python

    from sklearn.linear_model import LogisticRegression
    from cascade.utils.sklearn import SkModel

    model = SkModel(
        blocks = [
            LogisticRegression()
        ]
    )

2. Save it in Line
==================

.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("line", model_cls=SkModel)
    line.save(model)

3. Get rich metadata
====================

.. code-block:: python

    [
        {
            "name": "cascade.utils.sklearn.sk_model.SkModel",
            "description": None,
            "tags": [],
            "comments": [],
            "links": [],
            "type": "model",
            "created_at": "2024-09-03T19:36:49.346994+00:00",
            "metrics": [],
            "params": {},
            "pipeline": "Pipeline(steps=[('0', LogisticRegression())])",
            "path": "/home/ilia/local/cascade_proj/cascade_repo/cascade/docs/line/00000",
            "slug": "kickass_mayfly_of_pleasure",
            "saved_at": "2024-09-03T19:37:17.143040+00:00",
            "python_version": "3.11.0rc1 (main, Aug 12 2022, 10:02:14) [GCC 11.2.0]",
            "user": "ilia",
            "host": "my-pc-name",
            "cwd": "/home/ilia/local/cascade_proj/cascade_repo/cascade/docs",
            "git_commit": "07188653071cb73f8ede52ca09eea423b3ff2c0f",
            "git_uncommitted_changes": [
                "M cascade/docs/source/index.rst",
                "M cascade/docs/source/tutorials/tutorials.rst\n?? cascade/docs/line/"
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
* Elegancy - ML code should be about ML with minimum meta-code
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
