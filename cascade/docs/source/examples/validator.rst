Validator
=========
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
--------
:py:class:`cascade.meta.PredicateValidator`
:py:class:`cascade.meta.AggregateValidator`
:py:class:`cascade.meta.MetaValidator`