Models
######

Models are second part of two-fold Cascade concept scheme. They allow to wrap all models in
the same interface an treat models from different frameworks the same. It also brings the
order in the model-writing workflow since it forces you implement all abstract methods,
which include evaluation, saving and loading that are usually being omitted and forgotten.

Model
*****
:py:class:`cascade.models.Model`

Descendants of Model are wrappers around some inference and intended to use only in training context.
It is responsible for handling its own state - saving and loading it exactly as it is. It also should
perform evaluation and fill up its metrics.  

All this responsibilities form self-sufficient and independent model, which can be managed in more
abstract way.


ModelLine
*********
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
*********
:py:class:`cascade.models.ModelRepo`

ModelRepo constitutes a collection of lines.
Its meta can contain the information about the experiments in general and about things that are
applicable to all of the models. For example feature set, information about dataset (can be its meta)
or validation procedure.
