Track a file
############

This article is about saving an arbitrary file along with a
model in Cascade.

Every experiment can generate some files that need to be tracked. Cascade allows you to manage
file artifacts easily using ``Model`` API.

.. code-block:: python

    from cascade.utils.baselines import ConstantBaseline

    model = ConstantBaseline(constant=1)

    with open("file.txt", "w") as f:
        f.write("hello")

    model.add_file("file.txt")

This will copy ``file.txt`` into ``files`` folder within model's directory when a model is saved
by ``ModelLine``.

.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("file_test")
    line.save(model)

.. invisible-code-block: python

    import os
    assert os.path.exists("file_test/00000/files/file.txt")

You can check the folder ``file_test/00000/files`` to see ``file.txt`` copied there.

By using this tool you can log different file artifacts that are created during experiments.
For example images, audio files, plots, prediction results in tables or anything else.
