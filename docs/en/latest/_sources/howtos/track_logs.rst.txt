Track experiment logs with Cascade
##################################

Here we will discuss how to track your machine learning experiment logs using Cascade.

Minimal setup
=============

Suppose you already have a python script with some prints or other logging solutions.
Here is the minimal script with two lines of log.

.. code-block:: python

    if __name__ == "__main__":
        print("Hello!")
        print("I am example log")

Track your logs
===============

We will modify this script so that at each run it will save a new
model to a line of experiments with a log file.

.. code-block:: python

    from cascade.lines import ModelLine
    from cascade.models import BasicModel

    if __name__ == "__main__":
        print("Hello!")
        print("I am example log")

        model = BasicModel()
        model.add_log()

        line = ModelLine("log_tracking_example")
        line.save(model)

Notice that ``add_log`` does not accept any arguments. This is because the script
now expects to be run using ``cascade run`` that will capture the logs and do all
the magic necessary.

In the terminal we can do:

.. code-block:: bash

    cascade run track_logs.py --log

After that the special folder will be created that stores our logs automatically.
You can find the log files in ``<line_folder>/<model_folder>/files/cascade_run.log``

.. code-block:: text

    .
    ├── 00000
    │   ├── artifacts
    │   ├── files
    │   │   └── cascade_run.log
    │   ├── meta.json
    │   ├── model.pkl
    │   └── SLUG
    └── meta.json
