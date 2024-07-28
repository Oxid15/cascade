2. Metadata
===========

Data and model training in Cascade is based on metadata. It is the main
reason why wrappers should be created - they allow automatically capturing
info about underlying objects that can be logged and analyzed later.

To see what it looks like,
you can call `get_meta` method on a Cascade object. In the next
step we will try calling it on the pipeline that was made on
the :ref:`/tutorials/pipelines_basics.rst` step.

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
