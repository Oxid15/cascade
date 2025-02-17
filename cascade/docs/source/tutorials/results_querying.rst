Experiment results querying
###########################

When you have lots of experiments it becomes harder to analyze results by looking  into ``meta.json`` files.
One can also struggle to find some specific experiment results even knowing its slug or creation date.
This is where Cascade queries come in.

It is simple yet powerful Python-based query languare that works inside CLI. This tutorial will give overview of
its syntax and features.

Cascade query language
======================

Within the Cascade CLI there is a built in query language to get meta data from your repos and lines.

Here is full syntax reference:

.. code-block:: text

    cascade query COLUMN1 COLUMN2 ... \
    filter EXPR \
    sort EXPR desc \
    offset INT \
    limit INT \

Syntax tips
-----------

- After ``cascade query`` space-separated list of columns is required
- Use single quotation marks ``'`` to write expressions or columns if they contain spaces or special characters that may brake CLI command parsing

Basic query examples
====================

You can go to the desired directory - it can be a Workspace, Repo or Line and run for example

.. code-block:: bash

    cascade query slug created_at

This will list slugs and creation times for all of the models inside the folder you are currently in.

.. code-block:: text

    ─────────────────────────────────────────────────────────────────────────────────
    slug                                            created_at                       
    ─────────────────────────────────────────────────────────────────────────────────
    peridot_galago_of_endurance                     2024-06-28T10:31:59.682663+00:00 
    passionate_defiant_tarsier                      2024-06-28T10:31:59.687350+00:00 
    ─────────────────────────────────────────────────────────────────────────────────
    Finished: 2025-02-13 20:58:58.375351+03:00
    Time: 0.0018s

Columns
=======

The most basic case is the list of meta attribute names.

.. code-block:: bash

    cascade query slug name tags created_at saved_at

Columns can also be defined using simple expressions. Since meta is usually nested, you can access files using ``.``.

.. code-block:: bash

    cascade query params.lr params.training.batch_size params.inference.window_size

Since some of the files are lists, indexing is also allowed. Just use simple constant indices.

.. code-block:: bash

    cascade query 'metrics[0]' 'tags[1]'

You can combine those to access complex JSON objects.

.. code-block:: bash

    cascade query 'metrics[0].name' 'metrics[0].value'

.. note::

    At this moment columns do not support complex Python expressions, but this may be considered for later versions

Filtering
=========

After ``filter`` keyword you can write Python expressions that return ``True`` or ``False`` to filter results.

Expression should be valid Python with respect to the variables that you query. For example if you filter by slug,
then slug shoud appear in columns list.

.. code-block:: bash

    cascade query slug metrics filter 'slug == "passionate_defiant_tarsier"'

.. important::

    Use ``'`` single quotes to write complex expressions in command line

You can access complex objects in the same way as you query them.

.. code-block:: bash

    cascade query cascade query params.a filter 'params.a.b > 1'

Python expressions are fully supported, you can write relatively complex oneliners as long as you have everything you need in columns list.

.. code-block:: bash

    cascade query slug metrics filter 'min([m.value for m in metrics]) > 0.5'

Sorting
=======

Sorting works similar to filtering. You can pass arbitrary Python after ``sort`` and the results will be ordered.

.. code-block:: bash

    cascade query slug created_at sort created_at

Use ``desc`` to change the order to descending from the default ascending.

.. code-block:: bash

    cascade query slug created_at sort created_at desc

Limits and Offsets
==================

If you have many experiments you can use limits and offsets to see less results.
Pass ``int`` value after ``limit`` or ``offset`` keywords.

.. code-block:: bash

    cascade query slug limit 5

.. code-block:: bash

    cascade query slug offset 10 limit 5

.. important::

    Use ``offset`` before ``limit``

The keywords are most useful when sorting.

.. code-block:: bash

    cascade query slug created_at sort created_at desc limit 1
