Concepts
========
Here basic concepts of Cascade will be described. 

.. note::
    This section is close to the description of abstract classes, 
    but is not the documentation of particular code implementations, 
    rather the statement of key concepts and how things should be.

Data
----
The main focus of Cascade are data pipelines.
The library allows to construct them from many
interchangeable blocks, which are self-sufficient
in terms of gathering their own meta-data.

Dataset
~~~~~~~
:py:class:`cascade.data.Dataset`

Dataset - or its direct successor defines a data source.
For example in computer vision
it can be a folder of images. For tabular data it is the source 
table itself.

In terms of aggregating meta data it should be able to describe
itself and should do it in more details than 
any other pipeline block should.
Manually written documentation for Dataset is the best thing that
can be done and should be enforced.

Cascade has default builtin ways to write dataset doc. It is called
Data Card and it can be used with DataRegistrator

See also
~~~~~~~~
:py:class:`cascade.meta.DataCard`
:py:class:`cascade.meta.DataRegistrator`

Modifier
~~~~~~~~
:py:class:`cascade.data.Modifier`

Modifier - is a dataset that performs transformations on the dataset it accepts. 
It stores a reference to the previous dataset and is responsible for handling not only its own
meta data, but previous dataset's also. This mechanism allows to form
and trace a pipeline as a whole starting at its last block.

Models
------
Models are second part of two-fold Cascade concept scheme. They allow to wrap all models in
the same interface an treat models from different frameworks the same. It also brings the
order in the model-writing workflow since it forces you implement all abstract methods,
which include evaluation, saving and loading that are usually being omitted and forgotten.

Model
~~~~~
:py:class:`cascade.models.Model`

Descendants of Model are wrappers around some inference and intended to use only in training context.
It is responsible for handling its own state - saving and loading it exactly as it is. It also should
perform evaluation and fill up its metrics.  

All this responsibilities form self-sufficient and independent model, which can be managed in more
abstract way.

See also
~~~~~~~~
:py:class:`cascade.models.BasicModel`

ModelLine
~~~~~~~~~
:py:class:`cascade.models.ModelLine`

ModelLine is the entity that helps to track model's history in metrics and parameters.
This is a collection of models, which has its own meta, that describes the
collection as a whole.

It manages the storage of models and their meta so user don't have to care about how
models are stored.

Lines and Repos are very abstract and do not enforce some particular structure of experiments.
This means that depending on your workflow you can use lines as the track of a single models
through epochs or as a container for experiments with models with the same class and different
parameters.

ModelRepo
~~~~~~~~~
:py:class:`cascade.models.ModelRepo`

ModelRepo constitutes a collection of lines.
Its meta can contain the information about the experiments in general and about things that are
applicable to all of the models. For example feature set, information about dataset (can be its meta)
or validation procedure.

Meta
----
Meta data is the heart of Cascade and a part of its key principles. As the development continues
the set of instruments for working with meta data will be extended.

Validator
~~~~~~~~~
:py:class:`cascade.meta.Validator`

Validator is a special kind of Modifier that does not change the input, but 
performs checks on data. It can check each item in a dataset
or perform checks on the dataset as a whole.

You can subclass any of these classes to write your own data-validation unit to check 
some assumptions about dataset. Testing of data is crucial to ensure consistency,
speed up issue identification and ensure quality of data itself and hence quality of models.  

If you want some properties of your dataset to stay constant, you can add them in its meta and
check consistency automatically using mechanism of MetaValidator.

See also
~~~~~~~~
:py:class:`cascade.meta.PredicateValidator`
:py:class:`cascade.meta.AggregateValidator`
:py:class:`cascade.meta.MetaValidator`

Handler
~~~~~~~
:py:class:`cascade.base.MetaHandler`

MetaHandler is the lower-level abstraction layer for reading and writing meta. 
It accepts meta and can write and read it in any supported format abstracting from it.

Viewers
~~~~~~~
:py:class:`cascade.meta.MetaViewer`, :py:class:`cascade.meta.MetricViewer`, :py:class:`cascade.meta.HistoryViewer`, :py:class:`cascade.meta.DiffViewer`

Viewers are an interesting part of Cascade's set of tools. Their purpose is to give a user
the power to analyze their experiments and make sense of all meta that is stored after experiments.

MetaViewer is more high-level way to access meta than MetaHandler, but still abstract. It allows to read all 
meta-data in the folder and every child-folders and display it in the console.

MetricViewer is more specific - it reads `metrics` and `parameters` dicts in meta of models in each line and
build a table, which can be viewed in a variety of ways: it can be printed like pandas.DataFrame or plotted in the
web-view by plotly's Table.

Aside of that, MetricViewer has more general web-based interface. It still revolves around same table,
but provides analytical capabilities - plotting interactive scatterplots of metrics and parameters.

HistoryViewer is also a view around meta-data, but it builds a timeline of each line's progress in respect to
specific metric. It can be used to do manual feature selection and hyper-parameter tuning.

DiffViewer allows to see experiments individually and capture what changed between them to track indiviual changes.
It is useful if you do experiments manually and trying to analyze every step.
