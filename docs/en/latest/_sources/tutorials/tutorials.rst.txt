Tutorial
########

Tutorial is a set of lessons that will teach you
basics of Cascade. Lessons are connected in a single project
and depend on each other.
You can grasp the essence of how
you can use the library for your own projects, while
completing this one.

Installation
============

Install the latest version using pip

.. code-block:: bash

    pip install cascade-ml

Cascade has a set of optional dependencies, which can be installed with the following commands

.. code-block:: bash

    pip install cascade-ml[opencv]   # Use opencv as image backend
    pip install cascade-ml[pandera]  # Validate pandas dataframes with Pandera
    pip install cascade-ml[pil]      # Use Pillow as image backend
    pip install cascade-ml[pydantic] # Use data validation modifiers
    pip install cascade-ml[sklearn]  # Scikit-learn integration
    pip install cascade-ml[torch]    # PyTorch integration
    pip install cascade-ml[view]     # Cascade viewers based on dash
    pip install cascade-ml[all]      # Installs everything

If you have completed the tutorial you can see the :ref:`/howtos/howtos.rst` section
for more specific and complex workflows.

1. Pipelines basics
===================
In this tutorial you will learn basic pipeline building blocks of Cascade.
This is the first Cascade tutorial from a series. All of the tutorials are
meant to form a single project and can be thought of as a series of lessons.

.. Each lesson will come with a list of links for further reading or advanced
.. how-to guides on related topics.

Cascade pipelines allow building data processing routines from interchangeable
steps called ``Datasets`` and ``Modifiers``.

Datasets are the sources of data. In the first step let's make a Dataset
for ``digits`` from ``sklearn``.

.. code-block:: python

    from cascade.data import Dataset
    from sklearn.datasets import load_digits


    class DigitsDataset(Dataset):
        def __init__(self) -> None:
            self.x, self.y = load_digits(return_X_y=True)
            super().__init__()

        def __getitem__(self, index):
            return self.x[index], self.y[index]

        def __len__(self):
            return len(self.x)

Minimal setup for a Dataset is a ``__getitem__`` and ``__len__`` methods.
Now we can do basic access.

.. code-block:: python

    ds = DigitsDataset()
    print(ds[0])

Cascade Datasets are not only a system of data organization. They
allow using rich set of defaults for data manipulation.

.. code-block:: python

    import numpy as np
    from cascade.data import ApplyModifier


    def add_noise(x):
        return np.clip(x[0] + np.random.randint(-2, 2), 0, 15), x[1]


    ds_noise = ApplyModifier(ds, add_noise)

    print(ds_noise[0])

``Modifiers`` take datasets and transform their values.
In previous example we added noise to digits by using ``ApplyModifier``
and created new noisy dataset.

We can augment our data by concatenating those two datasets.

.. code-block:: python

    from cascade.data import Concatenator

    ds = Concatenator([ds, ds_noise])
    print(len(ds))

Further reading
***************
- :ref:`How to build a Pipeline</howtos/pipeline_building.ipynb>`
- :ref:`Dataset Zoo</modules/dataset_zoo.rst>`


2. Metadata
===========

Data and model training in Cascade is based on metadata. It is the main
reason why wrappers should be created - they allow automatically capturing
info about underlying objects that can be logged and analyzed later.

To see what it looks like,
you can call ``get_meta`` method on a Cascade object. In the next
step we will try calling it on the pipeline that was made on
the Pipelines step.

.. code-block:: python

    from pprint import pprint
    pprint(ds.get_meta())

.. code-block:: python

    [{'comments': [],
    'data': [[{'comments': [],
                'description': None,
                'len': 1797,
                'links': [],
                'name': '__main__.DigitsDataset',
                'tags': [],
                'type': 'dataset'}],
            [{'comments': [],
                'description': None,
                'len': 1797,
                'links': [],
                'name': 'cascade.data.apply_modifier.ApplyModifier',
                'tags': [],
                'type': 'dataset'},
                {'comments': [],
                'description': None,
                'len': 1797,
                'links': [],
                'name': '__main__.DigitsDataset',
                'tags': [],
                'type': 'dataset'}]],
    'description': None,
    'len': 3594,
    'links': [],
    'name': 'cascade.data.concatenator.Concatenator',
    'num_concatenated': 2,
    'tags': [],
    'type': 'dataset'}]

You can see all the pipeline stages in this metadata. It is a list of
dicts with JSON-serializable fields, each block in this list represents a pipeline step.

Datasets, Models and some other objects have metadata. It is a very flexible tool, that
can be easily customized to record valuable info about training process. We will see the power
of it in the following tutorials.


3. Experiments basics
=====================

Cascade provides a rich set of ML-experiment tracking tools.
You can easily track history of model changes, save and restore models
in a structured manner along with metadata.

In this step we create a wrapper around logistic regression model. Minimal setup
for the model is not strictly defined as in Dataset case. We define ``fit`` and ``predict``.
``BasicModel`` will handle everything else for us - like saving and loading for example.

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

We can create and fit the model now using the dataset from the Pipelines step.

.. code-block:: python

    model = LR("l2")
    model.fit(ds)

To track important hyperparameters and how they influence metrics, Cascade Models feature special field
called ``params``. This is an empty dict that you can fill with any (serializable) data. Cascade custom
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

Further reading
***************

- :ref:`How to train a model</howtos/model_training.ipynb>`
- :ref:`How to train a model with Trainer</howtos/model_training_trainers.ipynb>`


4. Custom Meta and Versioning
=============================

Metadata is a very flexible tool. It contains lots of useful info by default,
and can be customized.

In previous steps of the tutorial we created a dataset with an important
parameter, that was not recorded in our meta. If it changes in code, we wouldn't
see the effect in our logs. Now we can fix that issue.

.. code-block:: python

    from cascade.lines import DataLine

    ds.update_meta(
        {
            "long_description": "This is digits pipeline. It was augmented with some uniform noise",
            "noise_magnitude": NOISE_MAGNITUDE,
        }
    )

DataLines are the same thing as ModelLine but for data pipelines. You can use
them to track only metadata of your pipelines or even save and load whole pipelines
to reproduce an experiment.

.. code-block:: python

    dataline = DataLine("dataline")
    dataline.save(ds)

Unlike models, data pipelines are not numbered, but versioned.
Versions are derived from metadata of a pipeline and consist of two
parts - major and minor.

Let's see how it works.

.. code-block:: python

    version = dataline.get_version(ds)
    print(version) # 0.1

The starting version is ``0.1`` and then, when metadata changes,
parts of the version are bumped automatically. When saving
the version of a dataset that already exists, line will
notice that and overwrite older record with a new object.

.. code-block:: python

    ds.update_meta({"detail_i_almost_forgot": "Changes in meta bump minor version"})
    version = dataline.get_version(ds)
    print(version) # 0.2

    dataline.save(ds)

In previous example minor version was bumped by changing the part of the
pipeline's meta.

In the next one we add a new pipeline stage, which is what will bump
a major part of the version and we will see ``1.0``.

.. code-block:: python

    changed_ds = ApplyModifier(ds, add_noise)
    dataline.save(changed_ds)
    version = dataline.get_version(changed_ds)
    print(version) # 1.0

If we plug in an old dataset it will still get us the same version.
As long as meta is the same. Using version string we can load saved 
pipeline object from disk.

.. code-block:: python

    version = dataline.get_version(ds)
    print(version) # 0.2

    loaded_ds = dataline.load("0.2")
    version = dataline.get_version(loaded_ds)
    print(version) # 0.2


5. Metrics and Evaluation
=========================

Metrics are first-class citizens in Cascade.
For every ML-project they should be a central aspect.

Metric API is very flexible - you have a freedom to define metrics
in several ways. First case is the regular way metrics are usually defined
in projects - as functions.

Metric function can be passed in the default ``evaluate`` method of ``BasicModel``.
Evaluation of the model will return nothing, but fill its ``metrics`` field with a list
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
a descendant of ``cascade.metrics.Metric`` class. The one required method is ``compute``
that should return value and also set ``self.value``.

After that ``evaluate`` can be called with a list of ``Metric`` objects.

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

Metrics are saved and written in metadata automatically after calling ``evaluate``.

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
    'params': {'penalty': 'l2'},
    'path': '/home/ilia/local/cascade_proj/line/00001',
    'python_version': '3.11.0rc1 (main, Aug 12 2022, 10:02:14) [GCC 11.2.0]',
    'saved_at': '2024-07-28T14:47:32.902304+00:00',
    'slug': 'pompous_lori_from_lemuria',
    'tags': [],
    'type': 'model',
    'user': 'ilia'}]


6. Meta defaults
================

Cascade objects feature methods for managing some useful meta default fields.

For example descriptions - they can be useful if you want to convey basic information
about the model not only in code, but in saved metadata of this model.

.. code-block:: python

    model.describe("This is simple linear model")

Tags can be used to identify certain models, or filter them.

.. code-block:: python

    model.tag(["tutorial", "dummy"])

Links allow connecting a model to any relevant external media.
You can link a file using its URI, or a Cascade object like training data
or some other related model.

.. code-block:: python

    model.link(ds)
    model.link(name="training_file", uri=__file__)

There are also methods that allow removing certain fields. This part is mostly self-explanatory.

.. code-block:: python

    model.remove_tag("dummy")

.. code-block:: python

    model.remove_link("1")

Here we removed tag using its name and the first link using its ID. It is the dataset link, just for example.

.. code-block:: python

    pprint(model.get_meta())
    line.save(model)


7. Repos and Workspaces
=======================

This parts steps aside from previous task to demonstrate basic Cascade storage structure.
Lines are not the only tool to organize model storage. They themselves can be unified using Repo.
Repos can include both Data- and ModelLines. They can be used for access to a bunch of models and
are basic input for most of Cascade operations.

The following will give ``demo_repo/00000`` folder structure.

.. code-block:: python

    from cascade.repos import Repo

    demo_repo = Repo("demo_repo")
    demo_modelline = demo_repo.add_line(line_type="model")
    demo_dataline = demo_repo.add_line(line_type="data")

Sometimes Repos are piling up and to organize them effectively a Workspace was created. This is the highest unit
of experiment organization. Best practice will be having one Workspace per ML-project. Every container
share similar API. Using ``add_something`` methods you can create or just load an object if it already exists.

The following will give ``demo_workspace/repo/line`` folder structure.

.. code-block:: python

    from cascade.workspaces import Workspace

    ws = Workspace("demo_workspace")
    rp = ws.add_repo("repo")
    ln = rp.add_line("line")


8. CLI
======

Cascade features simple command line interface to manage storage
of your models, metadata and experiments. You can comment on models,
edit tags, descriptions and manage artifacts from the command line.

This tutorial is connected with Meta Defaults step
since CLI allows editing meta defaults without writing special scripts for it.

Go to the directory of previously created ``line`` and execute the following.

.. code-block:: bash

    cascade status

This is basic utility now just serves as a check that everything is okay with
you installation and directory. Cascade will look for ``meta.json`` file in the folder
you are running a command and if found, output short description of what is in this folder.

If everything is ok, previous command should output the following. If not, do not
hesitate filling a GitHub issue.

.. code-block:: text

    This is model_line of len 25

To print the contents of objects metadata you can visit a folder of an object and run.

.. code-block:: bash

    cascade cat

This will give you a nice prettyprint of ``meta.json`` that will look something like this.

.. code-block:: text

    [{'cascade_version': '0.14.0-alpha',
    'comments': [],
    'created_at': '2024-07-28 14:47:31.825546+00:00',
    'description': None,
    'item_cls': "<class '__main__.LR'>",
    'len': 25,
    'links': [],
    'name': "<class 'cascade.lines.model_line.ModelLine'>(3) items of <class "
            "'cascade.models.basic_model.BasicModel'>",
    'root': '/home/ilia/local/cascade_proj/line',
    'tags': [],
    'type': 'model_line',
    'updated_at': '2024-07-31 20:03:03.111970+00:00'}]

For different objects commands are similar. For example to list tags of the current objects you run.

.. code-block:: bash

    cascade tag ls

Since no tags in this line yet, it wil show an empty list.

.. code-block:: text

    []

Let's add two tags with one command and check.

.. code-block:: bash

    cascade tag add one two
    cascade tag ls

.. code-block::

    ['one', 'two']

Now we remove one tag and check again.

.. code-block:: bash

    cascade tag rm one
    cascade tag ls

.. code-block:: text

    ['two']

Comments are whole separate thing to consider in Cascade. They proved to be very useful for logging your progress
in a project. You can log your take on experiment results or your future plans inside a ModelLine, using comments as
notes. Or you can add sequential comments to a model so that they will be recorded in its metadata.

Comments differ from descriptions in this sense because they store username, host and date when comment was written.
This allows to have a log of notes with time that you can use to track your progress and if used on a shared machine
as a collaboration tool.

.. code-block:: bash

    cascade comment add
    cascade comment ls

After writing a command you will see a prompt for typing your comment in.
When done, press enter and check your comment by doing similar ls command.

.. code-block:: text

    1, ilia, my-pc-name   hello mlops
    a few seconds before


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
according to metric values. Since ``mv.table`` is a pandas DataFrame you can do your own analysis and visualizations.

.. code-block:: text

       line  num                       created_at                saved penalty        tags  comment_count  link_count name     value
    0  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0   f1  0.993826
    1  line    1 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2          []              0           0  acc  0.993879
    2  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1   f1  0.993826
    3  line    2 2024-08-01 20:02:31.589336+00:00  a few seconds after      l2  [tutorial]              0           1  acc  0.993879
    4  line    3 2024-08-01 20:02:37.266971+00:00  a few seconds after      l1          []              0           0  acc  0.994992
    5  line    3 2024-08-01 20:02:37.266971+00:00  a few seconds after      l1          []              0           0   f1  0.994946

Metric viewer as other Cascade viewers has a special dash-based web interface. You can install dash and run it with
CLI command or from the python code using ``serve()`` method.

After installing dash which is an optional dependency for web-based interfaces, you can run this.
The command will start a server on the port 8050 by default which you can open in your browser.
Go to ``localhost:8050`` to see the table of MetricViewer.

.. code-block:: text

    cascade view metric


11. Data Validation
===================

Data quality in ML projects is as important as the quality of the model.
This is why Cascade focuses on integrated and effortless data validation.

When the project grows, it becomes hard to control what is going on with
different Modifiers. Some may accept on certain formats of data and it is
hard to explicitly define those requirements within Modifier API.

This is where SchemaModifiers come in. They are special kind of Modifiers
that allow defining input schema for when we do ``__getitem__``.

Schema is defined using ``pydantic`` - an established tool for data validation
and also an optional dependency, you'll need to install it if you haven't yet.

The problem with our initial setup is that we operated with tuples, making
our schema implicit. If we were to reuse our datasets later, it would be hard
for us or other engineers to quickly grasp the return value layout and it will
also be easy to introduce errors in datasets that will be hard to debug.

Let's define a simple schema for our dataset from the beginning of the tutorial.

.. code-block:: python

    from pydantic import BaseModel

    class LabeledImage(BaseModel):
        image: np.ndarray
        label: int

        # This is for numpy array
        model_config = {"arbitrary_types_allowed": True}

Previous part is how we define schema in pydantic. You can use complex
schemas and Fields to place requirements on the input of your Modifiers.

Let's convert our dataset to a dataset with schema using this modifier.
It will just wrap the input into a model.

This is the entry point of data in our pipeline, so this part is important.
However, we also can ensure data integrity inside of the pipeline.

.. code-block:: python

    from cascade.data import SchemaModifier

    class LabeledImageModifier(SchemaModifier):
        def __getitem__(self, idx):
            image, label = self._dataset[idx]
            return LabeledImage(image=image, label=label)

Here we define a simple constant padding transform that uses our pydantic model
as an input schema for itself. Each time ``self._dataset[idx]`` is called, it will
automatically check the returned value against our model.

.. code-block:: python

    class Pad5(SchemaModifier):
        in_schema = LabeledImage

        def __getitem__(self, idx):
            item = self._dataset[idx]
            image = item.image.reshape((8, 8))
            h, w = image.shape
            new_image = np.zeros((h + 2 * 5, w + 2 * 5))
            new_image[5: 5 + h, 5: 5 + w] = image
            item.image = new_image.flatten()
            return item

Here we build a pipeline and augment our data using padding.

.. code-block:: python

    ds = LabeledImageModifier(ds)
    pad = Pad5(ds)

    ds = Concatenator([pad, ds])

Let's see the output.

.. code-block:: python

    print(ds[0])

Nothing special - validators are made to be effortless. They allow avoiding
writing manual checks in every instance of a dataset. We just define a schema
inside the whole class of datasets and they automatically check values that they
accept. And the return values stay the same.

Next example will show an actual case of input validation.

We will purposefully define some erroneous data to place before our padding transform.
In this case we mess up the type of a label. This seems to be very real practical situation
that would easily pass in our previous setup at would take some time to debug.

.. code-block:: python

    class FreakyImage(BaseModel):
        image: np.array
        label: str

        model_config = {"arbitrary_types_allowed": True}


    class EvilDataset(Dataset):
        def __getitem__(self, idx):
            return FreakyImage(image=np.zeros(18*18), label="hehe")

        def __len__(self):
            return 69

The following code will raise ValidationError, which we will catch and
display the latest message.

.. code-block:: python

    from cascade.data import ValidationError

    evil = EvilDataset()
    evil = Pad5(evil)

    try:
        evil[0]
    except ValidationError as e:
        print(e)


If we comment try/except out and see the whole traceback
(which is very long), we will see the following lines produced for us
by pydantic. 

.. code-block:: text

      Input should be a valid dictionary or instance of LabeledImage 
      [type=model_type, input_value=FreakyImage(image=array([...     0.]), label='hehe'), input_type=FreakyImage]

We can see that we didn't even get to the validation of a label. Our data was rejected
for being freaky enough without that.


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


13. Scikit-learn Integration
============================

Many of the things we implemented in this tutorial can be reused in similar projects.
This is one of the main principles on which Cascade was built. This is why most of the
things we done using ``sklearn`` library is already implemented in Cascade ``utils`` module.

In this tutorial we will overview ``scikit-learn`` library integration in Cascade. It features
default model class that can wrap pipelines of ``sklearn`` transformers and also special metric
wrapper for ``sklearn.metrics`` module.

Now we do not need to implement our own model wrapper or care about different methods. Everything
is already implemented in ``SkModel`` class. Notice how we pass ``blocks`` as a list of transforms.
The explicit use of keyword parameter here is required.

.. code-block:: python

    from cascade.utils.sklearn import SkModel

    model = SkModel(blocks=[LogisticRegression()])

The interface of this model's ``fit`` function accepts lists of elements.

.. code-block:: python

    ds = DigitsDataset()

    x = [item[0] for item in ds]
    y = [item[1] for item in ds]

    model.fit(x, y)

``SkMetric`` class provides a wrapper around ``metrics`` module. You can pass
a valid name from this module and it will be imported by Cascade for you.
Cascade also features some aliases for metrics. ``acc`` will import ``sklearn.metrics.accuracy_score``.

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

Notice how an artifact and a model are saved using the default implementation of ``save``
and ``save_artifact``.

.. code-block:: python

    last_model_dir = os.path.join(line.get_root(), line.get_model_names()[-1])
    print(os.listdir(last_model_dir))

.. code-block:: text

    ['model.pkl', 'meta.json', 'artifacts', 'SLUG']


What's Next
===========

Congratulations for completing the tutorial!

Now you can proceed to the :ref:`/howtos/howtos.rst` section
for specific usage recipes.
