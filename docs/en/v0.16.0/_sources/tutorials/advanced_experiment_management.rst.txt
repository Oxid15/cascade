Advanced Experiment Management
##############################

Lines are not the only tool to organize experiments. They themselves can be unified using ``Repo``.
Repos can include both ``Data``- and ``ModelLines``. In Cascade you cannot store models and
datasets in the same ``Line``, since each of the objects has its own .


Repos
=====

The following will give you ``demo_repo/00000`` folder structure.

.. code-block:: python

    from cascade.repos import Repo

    demo_repo = Repo("demo_repo")
    demo_modelline = demo_repo.add_line(line_type="model")
    demo_dataline = demo_repo.add_line(line_type="data")

Workspaces
==========

Sometimes Repos are piling up and to organize them effectively the ``Workspace`` was created. This is the highest unit
of experiment organization. 

.. note::

    Having one ``Workspace`` per ML-project can be considered the best practice.

All containers share similar API. Using ``add_<something>`` methods you can create or just load an object if it already exists.

The following will give ``workspace/repo/line/00000`` folder structure.

.. code-block:: python

    from cascade.workspaces import Workspace

    ws = Workspace("workspace")
    rp = ws.add_repo("repo")
    ln = rp.add_line("line")

    model = ln.create_model()
    ln.save(model)

Summary
=======

As a result Cascade features nested experiment organization.
When using the full set of levels you get:

.. code-block:: text

    .
    └── workspace
        ├── meta.json
        └── repo
            ├── line
            │   ├── 00000
            │   │   ├── meta.json
            │   │   └── SLUG
            │   └── meta.json
            └── meta.json
