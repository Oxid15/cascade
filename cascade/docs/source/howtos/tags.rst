Add Tags
########

.. meta::
   :description: Tag Cascade models, lines, repos, and other Traceable objects to organize and identify experiment results.
   :keywords: cascade, tags, Traceable, experiment tracking, model organization

Any Traceable object can be tagged. Tags are highly customizable. You can
use them in any way, building you own system.

For example one can version models, mark important results, best models for deploy, etc.
Since any Traceable is available you can tag lines and repos as well.

Tags are a list, but guaranteed to be unique when added using ``add_tag`` method.


.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("line")
    model = line.create_model()

CLI is the best way to use this feature.

Locate to the repo, line or model folder and then use:

.. code-block:: bash

    cascade tag add promising but_still

This will add two tags to the object.

And it has the same python API

.. code-block:: python

    model.tag("best") # Supports single item
    line.tag(["v1", "important"]) # and also iterables
