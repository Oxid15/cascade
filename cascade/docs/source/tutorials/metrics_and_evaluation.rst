5. Metrics and evaluation
=========================

Metrics are first-class citizens in Cascade.
For every ML-project they should be a central aspect.

Metric API is very flexible - you have a freedom to define metrics
in several ways. First case is the regular way metrics are usually defined
in projects - as functions.

Metric function can be passed in the default `evaluate` method of `BasicModel`.
Evaluation of the model will return nothing, but fill its `metrics` field with a list
of metrics.

.. code-block:: python

    from sklearn.metrics import f1_score


    def f1(gt, pred):
        return f1_score(gt, pred, average="macro")


    x = [item[0] for item in loaded_ds]
    y = [item[1] for item in loaded_ds]

    model.evaluate(x, y, [f1])

    pprint(model.metrics)

.. code-block:: python

    [Metric(name=f1, value=1.0, created_at="2024-07-29 19:41:09.344039+00:00")]

Let's try defining a metric in another, more flexible way. We need to implement
a descendant of `cascade.metrics.Metric` class. The one required method is `compute`
that should return value and also set `self.value`.

After that `evaluate` can be called with a list of `Metric` objects.

.. code-block:: python

    from cascade.metrics import Metric


    class Accuracy(Metric):
        def __init__(self):
            super().__init__(name="acc")

        def compute(self, gt, pred):
            self.value = sum([g == p for g, p in zip(gt, pred)]) / len(gt)
            return self.value


    model.evaluate(x, y, [Accuracy()])

    pprint(model.metrics)

.. code-block:: python

    [Metric(name=f1, value=1.0, created_at=2024-07-29 19:47:33.435828+00:00),
     Accuracy(name=acc, value=1.0, created_at=2024-07-29 19:47:33.437724+00:00)]

Metrics are saved and written in metadata automatically after calling `evaluate`.

.. code-block:: python

    line.save(model)
    pprint(line.load_model_meta(1))

.. code-block:: python

    [{'comments': [],
    'created_at': '2024-07-28T14:47:30.451860+00:00',
    'description': None,
    'host': 'my-pc-name',
    'links': [],
    'metrics': [{'created_at': '2024-07-28T14:47:32.860739+00:00',
                'name': 'f1',
                'value': 1.0},
                {'created_at': '2024-07-28T14:47:32.862089+00:00',
                'name': 'acc',
                'value': 1.0}],
    'name': '__main__.LR',
    'params': {},
    'path': '/home/ilia/local/cascade_proj/line/00001',
    'python_version': '3.11.0rc1 (main, Aug 12 2022, 10:02:14) [GCC 11.2.0]',
    'saved_at': '2024-07-28T14:47:32.902304+00:00',
    'slug': 'pompous_lori_from_lemuria',
    'tags': [],
    'type': 'model',
    'user': 'ilia'}]
