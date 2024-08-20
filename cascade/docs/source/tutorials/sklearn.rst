13. Scikit-learn Integration
============================

Many of the things we implemented in this tutorial can be reused in similar projects.
This is one of the main principles on which Cascade was built. This is why most of the
things we done using `sklearn` library is already implemented in Cascade `utils` module.

In this tutorial we will overview `scikit-learn` library integration in Cascade. It features
default model class that can wrap pipelines of `sklearn` transformers and also special metric
wrapper for `sklearn.metrics` module.

Now we do not need to implement our own model wrapper or care about different methods. Everything
is already implemented in `SkModel` class. Notice how we pass `blocks` as a list of transforms.
The explicit use of keyword parameter here is required.

.. code-block:: python

    from cascade.utils.sklearn import SkModel

    model = SkModel(blocks=[LogisticRegression()])

The interface of this model's `fit` function accepts lists of elements.

.. code-block:: python

    ds = DigitsDataset()

    x = [item[0] for item in ds]
    y = [item[1] for item in ds]

    model.fit(x, y)

`SkMetric` class provides a wrapper around `metrics` module. You can pass
a valid name from this module and it will be imported by Cascade for you.
Cascade also features some aliases for metrics. `acc` will import `sklearn.metrics.accuracy_score`.

If metrics require any keyword arguments, you can pass them at the creation time.

.. code-block:: python

    from cascade.utils.sklearn import SkMetric

    model.evaluate(
        x,
        y,
        [
            SkMetric("f1_score", average="macro"),
            SkMetric("acc"),
        ],
    )

Let's save the model and see how everything is handled automatically.

.. code-block:: python

    pprint(model.metrics)

    line.save(model)

.. code-block:: text

    [SkMetric(name=f1_score, value=1.0, created_at=2024-08-14 19:37:46.556587+00:00),
    SkMetric(name=acc, value=1.0, created_at=2024-08-14 19:37:46.556701+00:00)]

Notice how an artifact and a model are saved using the default implementation of `save`
and `save_artifact`.

.. code-block:: python

    last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
    print(os.listdir(last_model_dir))

.. code-block:: text

    ['model.pkl', 'meta.json', 'artifacts', 'SLUG']
