12. Artifacts and Files
=======================

Cascade wrappers serve to provide unified interface for different ML solutions
however in deployment scenarios they may obstruct underlying models.

To solve this problem artifacts were created. They are special methods that
when implemented save only the artifact of the model and not the wrapper.

In the next block we implement those methods - they accept a folder
(usually from ModelLine) and should save/load their artifact using it.

.. code-block:: python

    import os
    import pickle

    from sklearn.neural_network import MLPClassifier


    class NeuralNet(BasicModel):
        def __init__(self):
            self._model = MLPClassifier()
            super().__init__()

        def save_artifact(self, path: str) -> None:
            with open(os.path.join(path, "artifact.pkl"), "wb") as f:
                pickle.dump(self._model, f)

        def load_artifact(self, path: str) -> None:
            with open(os.path.join(path, "artifact.pkl"), "rb") as f:
                self._model = pickle.load(f)

We create and save this model in line.

.. code-block:: python

    nn = NeuralNet()
    line.save(nn)

To verify what is saved, let's peek into the folder of the model.
Special ``artifacts`` folder was created by the line where the model
saved its artifact.

.. code-block:: python

    last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
    print(os.listdir(last_model_dir))
    print(os.listdir(os.path.join(last_model_dir, "artifacts")))

.. code-block:: text

    ['model.pkl', 'meta.json', 'artifacts', 'SLUG']
    ['artifact.pkl']

Lots of cases may require linking files to the saved model. It can be
sample predictions, figures and plots, logs or anything you want to keep around
each model you save.

To allow this, Cascade features special method. Call ``add_file`` with a path
to the required file and it will be copied into ``files`` folder inside a folder
of the model in line.

Here we create dummy file with fake predictions and save it.

.. code-block:: python

    import json

    dummy_predictions = [0, 1, 2, 3]

    with open("dummy_predictions.json", "w") as f:
        json.dump(dummy_predictions, f)

We link the file by putting its path in ``add_file`` method. ModelLine
will copy it on save.

.. code-block:: python

    nn.add_file("dummy_predictions.json")
    line.save(nn)

Like previously we verify the files.

.. code-block:: python

    last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
    print(os.listdir(last_model_dir))
    print(os.listdir(os.path.join(last_model_dir, "files")))

.. code-block:: text

    ['model.pkl', 'meta.json', 'files', 'artifacts', 'SLUG']
    ['dummy_predictions.json']
