Comment on results of an experiment
###################################

Comments serve experiment tracking greatly since they allow record thoughts on
experiment results or expectations before them. They are more flexible, expressive,
and less formal than parameters for example. They also are a basis for collaboration
since multiple people can comment in a shared repo.

Add a Comment
*************

In Cascade you can have comments in any Traceable object.
Comments are recorded in meta. In case of disk-based Traceables
they are automatically synced to disk after creation.

.. code-block:: python

    from cascade.models import ModelLine

    line = ModelLine("line")
    model = line.create_model()

Notice how you can comment not only on models. Models will save
comments to disk only when saved, when lines and repos will
sync meta with disk automatically.

.. code-block:: python

    model.comment("This experiment will be the best")
    line.comment("Did you know that you can comment on any Traceable?")

Remove a Comment
****************

Every comment has an integer ID starting with ``1``, using which you can locate and
delete the comment.

.. code-block:: python

    model.remove_comment(1)


Using Cascade CLI
*****************

CLI is the best way to use this feature.

Locate to the repo, line or model folder and then use:

.. code-block:: bash

    cascade comment add

You will be prompted to enter a comment afterwards. Hit enter when you are ready.

You can display all the comments using:

.. code-block:: bash

    cascade comment ls

And delete using:

.. code-block:: bash

    cascade comment rm 1
