8. CLI
######

Cascade features simple command line interface to manage storage
of your models, metadata and experiments. You can comment on models,
edit tags, descriptions and manage artifacts from the command line.

This tutorial is connected with :ref:`/tutorials/meta_defaults.rst`
since CLI allows editing meta defaults without writing special scripts for it.

Go to the directory of previously created ``line`` and execute the following.

.. code-block:: bash

    cascade status

This is basic utility now just serves as a check that everything is okay with
you installation and directory. Cascade will look for ``meta.json`` file in the folder
you are running a command and if found, output short description of what is in this folder.

If everything is ok, previous command should output the following. If not, do not
hesitate filling a GitHub issue.

.. code-block:: text

    This is model_line of len 25

To print the contents of objects metadata you can visit a folder of an object and run.

.. code-block:: bash

    cascade cat

This will give you a nice prettyprint of ``meta.json`` that will look something like this.

.. code-block:: text

    [{'cascade_version': '0.14.0-alpha',
    'comments': [],
    'created_at': '2024-07-28 14:47:31.825546+00:00',
    'description': None,
    'item_cls': "<class '__main__.LR'>",
    'len': 25,
    'links': [],
    'name': "<class 'cascade.lines.model_line.ModelLine'>(3) items of <class "
            "'cascade.models.basic_model.BasicModel'>",
    'root': '/home/ilia/local/cascade_proj/line',
    'tags': [],
    'type': 'model_line',
    'updated_at': '2024-07-31 20:03:03.111970+00:00'}]

For different objects commands are similar. For example to list tags of the current objects you run.

.. code-block:: bash

    cascade tag ls

Since no tags in this line yet, it wil show an empty list.

.. code-block:: text

    []

Let's add two tags with one command and check.

.. code-block:: bash

    cascade tag add one two
    cascade tag ls

.. code-block::

    ['one', 'two']

Now we remove one tag and check again.

.. code-block:: bash

    cascade tag rm one
    cascade tag ls

.. code-block:: text

    ['two']

Comments are whole separate thing to consider in Cascade. They proved to be very useful for logging your progress
in a project. You can log your take on experiment results or your future plans inside a ModelLine, using comments as
notes. Or you can add sequential comments to a model so that they will be recorded in its metadata.

Comments differ from descriptions in this sense because they store username, host and date when comment was written.
This allows to have a log of notes with time that you can use to track your progress and if used on a shared machine
as a collaboration tool.

.. code-block:: bash

    cascade comment add
    cascade comment ls

After writing a command you will see a prompt for typing your comment in.
When done, press enter and check your comment by doing similar ls command.

.. code-block:: text

    1, ilia, my-pc-name   hello mlops
    a few seconds before
