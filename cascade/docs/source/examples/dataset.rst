Dataset
=======
:py:class:`cascade.data.Dataset`

The main focus of Cascade are data pipelines.
The library allows to construct them from many
interchangeable blocks, which are self-sufficient
in terms of managing their own meta-data.

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


Modifier
--------
:py:class:`cascade.data.Modifier`

Modifier - is a dataset that performs transformations on the dataset it accepts. 
It stores a reference to the previous dataset and is responsible for handling not only its own
meta data, but previous dataset's also. This mechanism allows to form
and trace a pipeline as a whole starting at its last block.


See also
--------
:py:class:`cascade.data.DataCard`
