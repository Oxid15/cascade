3. Experiments basics
=====================

Cascade provides a rich set of ML-experiment tracking tools.
You can easily track history of model changes, save and restore models
in a structured manner along with metadata.

In this step we create a wrapper around logistic regression model. Minimal setup
for the model is not strictly defined as in Dataset case. We define `fit` and `predict`.
`BasicModel` will handle everything else for us - like saving and loading for example.

.. code-block:: python

    from cascade.models import BasicModel
    from sklearn.linear_model import LogisticRegression


    class LR(BasicModel):
        def __init__(self, penalty):
            self.model = LogisticRegression(penalty=penalty)
            super().__init__()

        def fit(self, dataset):
            x, y = [], []
            for item in dataset:
                x.append(item[0])
                y.append(item[1])
            self.model.fit(x, y)

        def predict(self, x):
            return self.model.predict(x)

We can create and fit the model now using the dataset from :ref:`/tutorials/pipelines_basics.rst` step.

.. code-block:: python

    model = LR("l2")
    model.fit(ds)

To track important hyperparameters and how they influence metrics, Cascade Models feature special field
called `params`. This is an empty dict that you can fill with any (serializable) data. Cascade custom
JSON serializer can also serialize some non-default things like numpy arrays.

Here we fill our param externally, but could also do it above inside the class.

.. code-block:: python

    model.params["penalty"] = "l2"

Model lines are basic structured storage units in Cascade. They represent a lineage of
a model. Usually they represent a single training run, but can be used arbitrarily.

In this step we create a line and save our new model.

.. code-block:: python

    from cascade.lines import ModelLine

    line = ModelLine("line", model_cls=LR)
    line.save(model)

Lines handle storage of models and their metadata and can retrieve saved models by index or a name.

In the next step we load the model and infer it on a dataset.

The line knows little about models it manages - we provided a class of our model
to be able to restore it correctly when loading.

.. code-block:: python

    model = line.load(0)
    y = model.predict(ds)

    print(y[0], ds[0][1])

Lines also enhance model's meta by recording useful environment information.
Let's see what was saved automatically about this experiment. We load model
meta with a default line method.

.. code-block:: python

    from pprint import pprint
    pprint(line.load_model_meta(0))

.. code-block:: python

    [{'comments': [],
    'created_at': '2024-07-14T21:08:58.466812+00:00',
    'cwd': '/home/ilia/local/cascade_proj/cascade/cascade/docs/source/tutorials',
    'description': None,
    'git_commit': '62de43afb7dbf51afe2d08dd0825366661c76055',
    'git_uncommitted_changes': ['M '
                                'cascade/docs/source/tutorials/experiment_basics.rst',
                                'M cascade/docs/source/tutorials/tutorials.py',
                                'M cascade/docs/source/tutorials/tutorials.rst\n'
                                '?? cascade/docs/source/tutorials/line/'],
    'host': 'my-pc-name',
    'links': [],
    'metrics': [],
    'name': '__main__.LR',
    'params': {'penalty': 'l2'},
    'path': '/home/ilia/local/cascade_proj/cascade_repo/cascade/docs/source/tutorials/line/00000',
    'python_version': '3.11.0rc1 (main, Aug 12 2022, 10:02:14) [GCC 11.2.0]',
    'saved_at': '2024-07-14T21:09:01.453262+00:00',
    'slug': 'imperial_magenta_cheetah',
    'tags': [],
    'type': 'model',
    'user': 'ilia'}]
