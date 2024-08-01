9. Viewers
==========

After logging some amount of experiments with Cascade they can
become harder to analyze. To allow analysis of information in meta
Cascade features viewers. In this tutorial step basic MetricViewer will be
considered.

MetricViewer allows to map parameters of the model to its metrics.

.. code-block:: python

    from cascade.meta import MetricViewer

    mv = MetricViewer(line)
    print(mv.table)

In the output we can see all of the models we saved inside this line. Viewers usually accepts Repos, but can
work with single lines also.

This viewer reads all the metadata and build a pandas table around metric values.

.. code-block:: text

       line  num                       created_at                saved penalty        tags  comment_count  link_count name     value
    0  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0   f1  0.993826
    1  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0  acc  0.993879
    2  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1   f1  0.993826
    3  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1  acc  0.993879

Let's use metric viewer to identify the best parameter of penalty for this dataset. We will retrain the model,
evaluate it and save in the same way as before.

.. code-block:: python

    model = LR("l1")
    model.fit(ds)
    model.params["penalty"] = "l1"
    model.evaluate(x, y, [Accuracy(), f1])

    line.save(model)

Now we display the table once again.

.. code-block:: python

    mv = MetricViewer(line)
    print(mv.table)

It seems like l1 penalty gave slightly better results. Metric viewer can be used to identify optimal parameters
according to metric values. Since `mv.table` is a pandas DataFrame you can do your own analysis and visualizations.

.. code-block:: text

       line  num                       created_at                saved penalty        tags  comment_count  link_count name     value
    0  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0   f1  0.993826
    1  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0  acc  0.993879
    2  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1   f1  0.993826
    3  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1  acc  0.993879
    4  line    3 2024-08-01 20:02:37.266971+00:00  a few seconds after      l1          []              0           0  acc  0.994992
    5  line    3 2024-08-01 20:02:37.266971+00:00  a few seconds after      l1          []              0           0   f1  0.994946

Metric viewer as other Cascade viewers has a special dash-based web interface. You can install dash and run it with
CLI command or from the python code using `serve()` method.

After installing dash which is an optional dependency for web-based interfaces, you can run this.
The command will start a server on the port 8050 by default which you can open in your browser.
Go to `localhost:8050` to see the table of MetricViewer.

.. code-block:: text

    cascade view metric
