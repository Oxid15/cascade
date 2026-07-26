Use Cascade CLI
###############

Cascade has convenient command line interface to help
user perform some operations without writing Python for them.
Commands can be used to explore metadata, describe, tag and comment objects.
You can also run viewers and manage artifacts from CLI.

ClI Commands
============

Most commands are command groups. Each command
is described in detail below.

.. code-block:: bash

  artifact  # Manage artifacts
  cat       # Full meta data of the object
  comment   # Manage comments
  desc      # Manage descriptions
  migrate   # Automatic migration of objects to newer cascade versions
  status    # Short description of what is present in the current folder
  tag       # Manage tags
  view      # Different viewers

cascade artifact
****************

With this command you can remove all artifacts inside a container.
If your current directory is the model, then all model's artifacts will be
removed. If you are located inside a line, then artifacts of all models
inside this line will be removed. The same is true for repos and workspaces.

.. code-block:: bash

    cascade artifact rm

cascade cat
***********

Displays the metadata of the object in the current directory if it is run without
an argument.

.. code-block:: bash

    cascade cat

You can pass model slug to ``-p`` param and get metadata of the model if the model
with this slug is somewhere in the container. This will recursively search inside
subfolders so for example if you do ``cat -p SLUG`` inside of a repo it will search
in all of the lines.

.. code-block:: bash

    cascade cat -p SLUG

cascade comment
***************

Adds a comment to the current object. After invoking this
command you will be prompted to write a comment.

.. code-block:: bash

    cascade comment add

Displays a list of comments with user, host and time. For
containers also displays how many comments are inside of it.

.. code-block:: bash

    cascade comment ls

Removes a comment using its id.

.. code-block:: bash

    cascade comment rm ID

cascade desc
************

You can describe objects from command line with
the following command. After running it, you will be prompted
to write a description.

.. code-block:: bash

    cascade desc add

The following will remove description from the current object.

.. code-block:: bash

    cascade desc rm

cascade migrate
***************

Use this if your repo or line was created before version `0.13.0`
to migrate your metrics to a new format and continue using your old
repos with new Cascade.

.. code-block:: bash

    cascade migrate

cascade status
**************

Displays short info about the current folder.

.. code-block:: bash

    cascade status

cascade tag
***********

You can add one of multiple tags by passing them after add command.

.. code-block:: bash

    cascade tag add TAG1, TAG2, ...

This will display a list of tags. The order may not be preserved.

.. code-block:: bash

    cascade tag ls

This will remove given tags.

.. code-block:: bash

    cascade tag rm TAG1, TAG2, ...

cascade view
************

To use this feature install ``dash`` separately or by using ``pip install cascade[view]``.
Locate the workspace, repo or line (not every viewer can work in all of those) and run
the following commands.

This will run diff viewer, which can be used to display diffs between two meta files.

.. code-block:: bash

    cascade view diff

This will run history viewer with plots of metric values through time.

.. code-block:: bash

    cascade view history

This will run basic metric viewer, which is a table view of metrics and parameters inside a repo.

.. code-block:: bash

    cascade view metric
