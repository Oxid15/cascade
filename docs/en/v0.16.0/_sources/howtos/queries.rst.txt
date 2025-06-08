Common query use cases
######################

Cascade has special query language for command line. You can ``cd`` to your repo or line and
write ``cascade query`` to get information without manually visiting each ``meta.json`` file.
Here you can find examples of queries, that may be adapted to frequent use cases.

For a full queriyng tutorial you can proceed to :ref:`/tutorials/results_querying.rst`

Getting experiment knowing a slug
=================================

.. code-block:: bash

    cascade query slug created_at filter 'slug == "brave_solemn_urchin"'

Listing latest metric values
============================

.. code-block:: bash

    cascade query '[m for m in metrics if m.name == "F1"][0].value' created_at sort created_at desc

Top-5 experiments by accuracy
=============================

.. code-block:: bash

    cascade query slug created_at sort '[m for m in metrics if m.name == "acc"][0].value' limit 5

Filtering by tag
----------------

.. code-block:: bash

    cascade query slug filter '"prod" in tags'

Finding experiments by description
==================================

.. code-block:: bash

    cascade query slug description filter 'description.startswith("LR scheduler experiment")'

Filter by linked dataset
========================

.. code-block:: bash

    cascade query slug filter 'any([l.name == "mnist" for l in links])'

Find experiments made on a specific git commit
==============================================

.. code-block:: bash

    cascade query git_commit filter 'git_commit.startswith("4870b9")'

Compare two dataset versions
============================

.. code-block:: bash

    cascade query slug metrics[0].value filter 'links[0].version in ("v1", "v2")' sort 'links[0].version'
