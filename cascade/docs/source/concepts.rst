Concepts
========
Here basic concepts of Cascade will be described. 

.. note::
    This section is close to the description of abstract classes, 
    but is not the documentation of particular code implementations, 
    rather the statement of key concepts and how things should be.

Data
----
The main focus of Cascade are data pipelines. It allows to construct them from many
interchangeable blocks, which are self-sufficient in terms of logging their own meta-data.

Dataset
~~~~~~~
:py:class:`cascade.data.Dataset`

Dataset - or its direct successor defines a data source. For example in computer vision
pipeline it can be a folder of images or it can constitute different folders in case of
classification task.  
It should be able to describe itself and should do it in more details than 
any other pipeline block should. It can describe all files in it and aggregate info about them.
Manually written documentation for Dataset is the best thing that can be done and should be enforced.

Modifier
~~~~~~~~
:py:class:`cascade.data.Modifier`

Modifier - is a dataset that performs transformations on the dataset it accepts. 
It stores a reference to the previous dataset and is responsible for handling not only its own
meta-data, but previous dataset's also. This mechanism allows to form and trace a pipeline.

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

ModelLine
~~~~~~~~~
:py:class:`cascade.models.ModelLine`
ModelLine is the entity that helps to track one model's progress in metrics and parameters.
This is a collection of models of the same class, which has its own meta, that describes the
collection as a whole.  

It manages the saving and loading of models and their meta.

ModelRepo
~~~~~~~~~
:py:class:`cascade.models.ModelRepo`
ModelRepo constitutes a collection of ModelLines. A collection of experiments with its lines of models.
Its meta can contain the information about the experiments in general and about things that are
applicable to all of the models. For example feature set, information about dataset (can be its meta)
or validation procedure.

Meta
----
Meta data is the heart of Cascade and a part of its key principles. As the development continues
the set of instruments for working with meta data should extend.

Validator
~~~~~~~~~
:py:class:`cascade.meta.Validator`
Validator is a special kind of Modifier that performs checks on data. It can check each item in a dataset
or perform checks on the dataset as a whole. For implementation of these cases see 
:py:class:`cascade.meta.PredicateValidator` and :py:class:`cascade.meta.AggregateValidator`.

You can subclass any of these classes to write your own data-validation unit to check 
some assumptions about dataset. Testing of data is crucial to speed up finding issues in it,
ensure quality of data hence quality of models.  

If you want some properties of your dataset to stay constant, you can add them in its meta and
check consistency automatically using mechanism of MetaValidator.
See it in :py:class:`cascade.meta.MetaValidator`.

Viewers
~~~~~~~
:py:class:`cascade.meta.MetaViewer`, :py:class:`cascade.meta.MetricViewer`

.. important::
    This section is WIP, will be filled in following releases, see the documentation for details
    about this concept!

Handler
~~~~~~~
:py:class:`cascade.meta.MetaHandler`

.. important::
    This section is WIP, will be filled in following releases, see the documentation for details
    about this concept!
