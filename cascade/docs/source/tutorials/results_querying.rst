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
- At this point the language does not support row-level aggregation so some complex use cases may not be achieved

Querying
========

You can go to the desired directory - it can be a Workspace, Repo or Line and run for example

.. code-block:: bash

    cascade query slug created_at

This will list slugs and creation times for all of the models inside the folder you are currently in.

You should see something like this - depending on your terminal width the size of the table will be adapted.

.. code-block:: text

    ─────────────────────────────────────────────────────────────────────
    slug                             created_at                          
    ─────────────────────────────────────────────────────────────────────
    adamant_flat_bat                 2024-04-06T19:28:33.723569+00:00    
    brave_solemn_urchin              2024-04-06T19:37:13.888717+00:00    
    diamond_orca_of_happiness        2024-04-06T19:50:07.920992+00:00    
    athletic_muscular_gibbon         2024-04-06T19:28:33.723182+00:00    
    sparkling_rugged_coucal          2024-04-06T19:37:13.888360+00:00    
    singing_nifty_turkey             2024-04-06T19:50:07.920675+00:00    
    ─────────────────────────────────────────────────────────────────────
    Finished: 2025-02-22 23:18:25.883223+03:00
    Returned rows: 6
    Time: 0.0041s


Columns
=======

The most basic case is the list of meta attribute names.

.. code-block:: bash

    cascade query slug name tags created_at saved_at

Columns can also be defined using Python expressions. Since meta is usually nested, you can access files using ``.``.

.. code-block:: bash

    cascade query params.lr params.training.batch_size params.inference.window_size

Since some of meta fields are lists, indexing is also allowed.

.. code-block:: bash

    cascade query 'metrics[0]' 'tags[1]'

You can combine those to access complex JSON objects.

.. code-block:: bash

    cascade query 'metrics[0].name' 'metrics[0].value'


Filtering
=========

After ``filter`` keyword you can write Python expressions that return ``True`` or ``False`` to filter results.

Expression should be valid Python with respect to meta of models you query. If something is wrong or the key does not
exist, None will be returned.

For additional safety some builtins are not allowed. Additional evals or execs, imports and file openings will not work.

.. code-block:: bash

    cascade query slug metrics filter 'slug == "passionate_defiant_tarsier"'

.. important::

    Use ``'`` single quotes to write complex expressions in command line

You can access complex objects in the same way as in columns expressions.

.. code-block:: bash

    cascade query cascade query params.a filter 'params.a.b > 1'

Python expressions are fully supported, you can write relatively complex oneliners.

.. code-block:: bash

    cascade query slug metrics filter 'min([m.value for m in metrics]) > 0.5'

Sorting
=======

Sorting works similar to filtering. You can pass arbitrary Python after ``sort`` and the results will be ordered
by the return values for each model's meta.

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

Limit keywords are most useful when sorting.

.. code-block:: bash

    cascade query slug sort created_at desc limit 1


Common query use cases
======================

Getting experiment knowing a slug
---------------------------------

.. code-block:: bash

    cascade query slug created_at filter 'slug == "brave_solemn_urchin"'

Listing latest metric values
----------------------------

.. code-block:: bash

    cascade query '[m for m in metrics if m.name == "F1"][0].value' created_at sort created_at desc

Top-5 experiments by accuracy
-----------------------------

.. code-block:: bash

    cascade query slug created_at sort '[m for m in metrics if m.name == "acc"][0].value' limit 5

Filtering by tag
----------------

.. code-block:: bash

    cascade query slug filter '"prod" in tags'

Finding experiments by description
----------------------------------

.. code-block:: bash

    cascade query slug description filter 'description.startswith("LR scheduler experiment")'

Filter by linked dataset
------------------------

.. code-block:: bash

    cascade query slug filter 'any([l.name == "mnist" for l in links])'

Find experiments made on a specific git commit
----------------------------------------------

.. code-block:: bash

    cascade query git_commit filter 'git_commit.startswith("4870b9")'

Compare two dataset versions
----------------------------

.. code-block:: bash

    cascade query slug metrics[0].value filter 'links[0].version in ("v1", "v2")' sort 'links[0].version'

Notes on syntax, imports and extensibility
==========================================

For some specific use cases it can be hard to leverage pure Python without using some
libraries. Some cases might require some Cascade-side syntax tweaks
(like it was done with ``.`` syntax for accessing nested meta).
As the solution evolves some of those could be considered (via plugins mechanism or some
other). Consider writing an issue if you have ideas!
