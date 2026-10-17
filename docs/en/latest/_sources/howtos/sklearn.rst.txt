Track scikit-learn experiment
#############################

With Cascade you can track any ML experiment.
And the workflow is usually the same for a single library.

Cascade respects the tools ML engineers use every day and was built to
simplify repetitive work.
This is the reason why it features scikit-learn integration - 
it simplifies experiment tracking a lot.

Everything is located in ``cascade.utils.sklearn``.

.. code-block:: python

    from cascade.utils.sklearn import SkModel
    from sklearn.feature_selection import SelectKBest
    from sklearn.svm import SVC

``SkModel`` class accepts a list of ``Pipeline`` blocks from ``scikit-learn``.
Everything you can put into a pipeline, you can pass as a list to the Cascade
wrapper.

.. note::
    Remember to use the keyword ``blocks``, it will not work without it!

.. code-block:: python

    k_best = 2

    model = SkModel(
        blocks=[
            SelectKBest(k=k_best),
            SVC(),
        ],
        k=k_best,
    )

Notice how ``k_best`` was passed both into a transform and wrapper.
This is how ``SkModel`` gets the parameters to track. You can pass
anything else you want to be tracked as parameters. This may change to
an automatic parameters tacking in future versions.

After creating you can use the wrapper as you would 
use ``sklearn`` estimator.

.. code-block:: python

    from sklearn.datasets import load_iris

    iris = load_iris()

For example fit will look like this.

.. code-block:: python

    model.fit(iris.data, iris.target)

And predict like this. Nothing unusual.

.. code-block:: python

    model.predict([iris.data[0]]), iris.target[0]

Cascade allows to conveniently use metrics in evaluation.
You can create metrics by using alias like \"acc\" or \"f1\" here or
using a name that you would import from ``sklearn.metrics`` module.

.. code-block:: python

    from cascade.utils.sklearn import SkMetric

    metrics = [
        SkMetric("acc"),
        SkMetric("f1", average="macro"),
        SkMetric("precision_score", average="macro"),
        SkMetric("recall_score", average="macro"),
    ]

To evaluate a model, pass the data and a list of metric objects.

.. code-block:: python

    model.evaluate(iris.data, iris.target, metrics=metrics)

Evaluate will not return anything, instead it will fill metrics list
inside a model.

.. code-block:: python

    from pprint import pprint

    pprint(model.metrics)


.. code-block:: text

    [SkMetric(name=acc, value=0.9533333333333334, created_at=2024-09-16 19:06:05.354980+00:00),
     SkMetric(name=f1, value=0.9532912954992826, created_at=2024-09-16 19:06:05.355031+00:00),
     SkMetric(name=precision_score, value=0.9543690619563763, created_at=2024-09-16 19:06:05.355048+00:00),
     SkMetric(name=recall_score, value=0.9533333333333333, created_at=2024-09-16 19:06:05.355060+00:00)]

Now to track all the results we can save the model to the line.

.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("sklearn_demo", model_cls=SkModel)
    line.save(model)
