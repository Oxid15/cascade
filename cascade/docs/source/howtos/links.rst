Link anything
#############

Linking one object to an another is a mechanic that was
introduced in ``0.13.0``.

Its main purpose is to enable ability to tie one object to the other
without using custom meta editing.

This enables for example tracking what data was used to train which model.

Link is a separate object that contains everything that is needed to
store about another object.

Given a Traceable one can link to it:
  1. Another Traceable
  2. An object that has a URI (a file or folder, local or remote) for example to reference some data
  3. Custom object with a name (and optionally a meta)


.. code-block:: python

    from cascade.models import Model
    from cascade.data import Dataset

    ds = Dataset()
    model = Model()

    # Will create a Link in model to the ds
    model.link(ds)

    # Will make this path absolute automatically if it exists
    model.link(name="local_dataset", uri="./my_local_data")


If you link a Traceable, you may choose to include its full meta or just use essential fields from it.

.. code-block:: python

    from cascade.models import Model
    from cascade.data import Dataset

    ds = Dataset()
    model = Model()

    model.link(ds, include=False)
