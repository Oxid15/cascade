How-to guides
#############

This is a page of how-to guides. Guides are basically answers to the "How to ... with Cascade" type of questions.
They should be practical and may require some background knowledge of Cascade.

If you are new to the library, you may want to start from the :ref:`/tutorials/tutorials.rst` page.

Pipelines
*********

.. grid:: 1

    .. grid-item::
        .. card:: Build a pipeline
            :link: /howtos/pipeline_building.ipynb
            :link-type: ref

            How to build data processing pipelines with cascade.data module

Experiment tracking
*******************

.. grid:: 1

    .. grid-item::
        .. card:: Track model training experiment
            :link: /howtos/model_training.ipynb
            :link-type: ref

            How to conduct experiments with Cascade

    .. grid-item::
        .. card:: Use a Trainer
            :link: /howtos/model_training_trainers.ipynb
            :link-type: ref

            How to make model training even easier with Trainers

    .. grid-item::
        .. card:: Track a file
            :link: /howtos/track_a_file.rst
            :link-type: ref

            How to log files along with saved model

Integrations
************

.. grid:: 1

    .. grid-item::
        .. card:: scikit-learn
            :link: /howtos/sklearn.rst
            :link-type: ref

            Effectively track your sklearn experiments

    .. grid-item::
        .. card:: PyTorch

            :bdg-info:`To be written soon!`


Experiment management
*********************

.. grid:: 1

    .. grid-item::
        .. card:: Link Dataset to a Model
            :link: /howtos/links.rst
            :link-type: ref

            You can link anything to anything basically

    .. grid-item::
        .. card:: Comment on results of an experiment
            :link: /howtos/comments.rst
            :link-type: ref

            Filling bare numbers with some meaning and starting discussions

    .. grid-item::
        .. card:: Add Tags
            :link: /howtos/tags.rst
            :link-type: ref

            It is about building your own system


.. toctree::
    :maxdepth: 1
    :hidden:

    pipeline_building.ipynb
    model_training.ipynb
    model_training_trainers.ipynb
    track_a_file
    links
    comments
    tags
