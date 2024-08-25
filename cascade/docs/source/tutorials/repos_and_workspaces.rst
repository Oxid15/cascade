7. Repos and Workspaces
=======================

This parts steps aside from previous task to demonstrate basic Cascade storage structure.
Lines are not the only tool to organize model storage. They themselves can be unified using Repo.
Repos can include both Data- and ModelLines. They can be used for access to a bunch of models and
are basic input for most of Cascade operations.

The following will give ``demo_repo/00000`` folder structure.

.. code-block:: python

    from cascade.repos import Repo

    demo_repo = Repo("demo_repo")
    demo_modelline = demo_repo.add_line(line_type="model")
    demo_dataline = demo_repo.add_line(line_type="data")

Sometimes Repos are piling up and to organize them effectively a Workspace was created. This is the highest unit
of experiment organization. Best practice will be having one Workspace per ML-project. Every container
share similar API. Using ``add_something`` methods you can create or just load an object if it already exists.

The following will give ``demo_workspace/repo/line`` folder structure.

.. code-block:: python

    from cascade.workspaces import Workspace

    ws = Workspace("demo_workspace")
    rp = ws.add_repo("repo")
    ln = rp.add_line("line")
