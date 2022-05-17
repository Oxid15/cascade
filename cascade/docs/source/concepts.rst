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



Sampler
~~~~~~~
:py:class:`cascade.data.Sampler`


Models
------

Model
~~~~~
:py:class:`cascade.models.Model`

ModelLine
~~~~~~~~~
:py:class:`cascade.models.ModelLine`

ModelRepo
~~~~~~~~~
:py:class:`cascade.models.ModelRepo`

Meta
----

Validator
~~~~~~~~~
:py:class:`cascade.meta.Validator`

Viewers
~~~~~~~
:py:class:`cascade.meta.MetaViewer`

Handler
~~~~~~~
:py:class:`cascade.meta.MetaHandler`
