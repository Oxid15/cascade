6. Meta defaults
================

Cascade objects feature methods for managing some useful meta default fields.

For example descriptions - they can be useful if you want to convey basic information
about the model not only in code, but in saved metadata of this model.

.. code-block:: python

    model.describe("This is simple linear model")

Tags can be used to identify certain models, or filter them.

.. code-block:: python

    model.tag(["tutorial", "dummy"])

Links allow connecting a model to any relevant external media.
You can link a file using its URI, or a Cascade object like training data
or some other related model.

.. code-block:: python

    model.link(ds)
    model.link(name="training_file", uri=__file__)

There are also methods that allow removing certain fields. This part is mostly self-explanatory.

.. code-block:: python

    model.remove_tag("dummy")

.. code-block:: python

    model.remove_link(0)

Here we removed tag using its name and the first link using its index. It is the dataset link, just for example.

.. code-block:: python

    pprint(model.get_meta())

    line.save(model)
