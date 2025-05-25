Cascade UI
##########

Cascade UI is a web-based dashboard for your machine learning experiments.
It provides a visual overview of your experiment results,
metadata, parameters, metrics and more.

This single interface is a replacement for dash-based Viewers, that
were used previously to visualize results.

Installation
============

Install the latest version using pip

.. code-block:: bash

    pip install cascade-ui

Basic Usage
===========

You can run Cascade UI with a simple CLI command.
Navigate to the Workspace folder or a parent folder to your repo and run.

.. code-block:: bash

    cascade ui

The command will open a server on local port 8000. If you open a link in
your browser you will see your workspace overview.

.. image:: imgs/workspace-page.png
  :alt: Workspace page of Cascade - Small scale MLOps library

You can interact with the workspace itself or go deeper into any repo.

Repos
=====

Repo page features a table of lines with their basic info.

.. image:: imgs/repo-page.png
  :alt: Repo page of Cascade - Small scale MLOps library

Lines
=====

Line page features customizable table with the info about models, comments and plots.

.. image:: imgs/line-page.png
  :alt: Line page of Cascade - Small scale MLOps library

Select columns
--------------

You can select columns from the list and request them from model's meta.

.. image:: imgs/line-custom-table.png
  :alt: Table customization page of Cascade - Small scale MLOps library

Plots
-----

Inside each line you can visualize the change of metrics.

.. image:: imgs/line-plots.png
  :alt: Line plots page of Cascade - Small scale MLOps library

Models
======

Model page provides detailed overview of machine learning 
experiment metadata, tracked parameters and metrics.

.. image:: imgs/model-page.png
  :alt: Model page of Cascade - Small scale MLOps library

Configs
-------

Here you can see configs produced by Cascade's configuration management
system. If your model has a config saved it will be displayed here.

.. image:: imgs/model-config.png
  :alt: Model config page of Cascade - Small scale MLOps library

Logs
----

If you used ``cascade run`` with log tracking, you will be able to see your logs here.

.. image:: imgs/model-logs.png
  :alt: Model logs page of Cascade - Small scale MLOps library

Comments
========

You can comment on each container using UI too.

.. image:: imgs/model-comments.png
  :alt: Model comments page of Cascade - Small scale MLOps library
