Artifacts
=========

Artifacts are files that are results of model training, evaluation, prediction, etc.

Model artifacts
---------------

In default model wrappers like `TorchModel` and `SkModel` model files are saved automatically
in `artifacts` folder within model's directory.

Although those are wrappers, only clean artifacts are saved without any wrappers, which are
saved separately.

File artifacts
--------------

Every experiment can generate some files that need to be tracked. Cascade allows you to manage
file artifacts easily using model's API.

.. code-block:: python

    from cascade.models import Model

    model = Model()

    with open("file.txt", "w") as f:
        f.write("hello")
    
    model.add_file("file.txt")

This will copy `file.txt` into `files` folder within model's directory.

Model's work with artifacts
===========================

.. note::

    This section will come useful if you are writing your own model's wrapper.
    In all Cascade's default wrappers everything is already handled.

Every `Model` has two methods `save()` and `save_artifact()`. Those methods come in separation
since it is better to separate tracking wrapper from the actual artifact.
To save up space when saving model is decoupled from wrapper, since two methods are usually
called at the same time.

See also
========
:py:class:`cascade.utils.torch.TorchModel`
:py:class:`cascade.utils.sklearn.SkModel`
