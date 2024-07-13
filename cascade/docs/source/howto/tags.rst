Tags
====

Any Traceable object can be tagged. Tags are highly customizable in terms of
the categorization system one can build using them.

For example one can version models, mark important results, best models for deploy, etc.
Since any Traceable is available you can mark lines and repos as well.

Tags are a list, but guaranteed to be unique when added using `add_tag` method.


.. code-block:: python

    from cascade.models import ModelLine

    line = ModelLine("line")
    model = line.create_model()

CLI is the best way to use this feature

Locate to the repo, line or model folder and then use:

.. code-block:: bash

    cascade tag add promising but_still

This will add two tags to the object.

And it has the same python API

.. code-block:: python

    line.tag("best") # Supports single item
    line.tag(["v1", "important"]) # and also iterables
