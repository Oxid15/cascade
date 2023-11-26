Comments
========

Comments serve experiment tracking a lot since they allow record thoughts on
experiment results or expectations before them. They also are a basis for collaboration
since multiple people can comment on a shared machine.
In Cascade you can comment any Traceable object.

.. code-block:: python

    from cascade.models import ModelLine

    line = ModelLine("line")
    model = line.create_model()

CLI is the best way to use this feature

Locate to the repo, line or model folder and then use:

.. code-block:: bash

    cascade comment add

Although it has the same python API

.. code-block:: python

    line.comment("This experiment will be the best")
