Experiment basics
=================

Cascade provides a rich set of ML-experiment tracking tools.


.. code-block:: python

    from cascade.models import BasicModel
    from sklearn.linear_model import LogisticRegression


    class LR(BasicModel):
        def __init__(self):
            self.model = LogisticRegression()
            super().__init__()

        def fit(self, dataset):
            x, y = [], []
            for item in dataset:
                x.append(item[0])
                y.append(item[1])
            self.model.fit(x, y)

        def predict(self, dataset):
            return self.model.predict([item[0] for item in dataset])

We can create and fit the model now using the dataset from :ref:`/tutorials/pipelines.rst` step.

.. code-block:: python

    model = LR()
    model.fit(ds)

Model lines 

.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("line", model_cls=BasicModel)
    line.save(model)

Lines handle storage of models and can retrieve saved models by index or a name.

.. code-block:: python

    model = line.load(0)
    y = model.predict(ds)

    print(y[0], ds[0][1])
