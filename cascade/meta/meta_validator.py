import os
from hashlib import md5
from deepdiff import DeepDiff
from . import Validator, DataValidationException
from ..data import Dataset
from ..base import MetaHandler


class MetaValidator(Validator):
    """
    Standard validator that saves the dataset's meta
    on the first run and checks if it is consistent
    on the following runs.

    `MetaValidator` is a `Modifier` that checks data
    consistency in several pipeline runs. If pipeline of data
    processing consists of cascade Datasets it uses meta of all
    pipelines to ensure that data is unchanged.

    Capabilities of this validator are as powerful as pipelines meta and
    is defined by extending `get_meta` methods.

    Example
    -------
    >>> from cascade.tests import NumberDataset
    >>> from cascade.data import Modifier
    >>> from cascade.meta import MetaValidator
    >>> ds = NumberDataset([1,2,3,4])  # Define dataset
    >>> ds = Modifier(ds)  # Wrap some modifiers
    >>> ds = Modifier(ds)
    >>> MetaValidator(ds) # Add validation by passing ds, but with no assigning to use data later

    In this example on the first run validator saves meta of this pipeline, which looks
    something like this:

    >>> [{'len': 4, 'name': 'cascade.data.dataset.Modifier'},
    >>> {'len': 4, 'name': 'cascade.data.dataset.Modifier'},
    >>> {'len': 4, 'name': 'cascade.tests.number_dataset.NumberDataset'}]


    On the second run of the pipeline it computes pipeline's meta and then
    meta's hash based on the names of blocks. This is needed to check if
    pipeline structure is changed.
    If it founds that pipeline has the same structure, then meta dicts are
    compared using `deepdiff` and if everything is ok it returns.

    If the structure of pipeline is different it saves new meta file.

    Raises
    ------
    cascade.meta.DataValidationException

    See also
    --------
    cascade.data.Modifier
    """
    def __init__(self, dataset: Dataset, root=None) -> None:
        super().__init__(dataset, lambda x: True)
        self.mh = MetaHandler()
        if root is None:
            root = './.cascade'
            os.makedirs(root, exist_ok=True)
        self.root = root

        meta = self._dataset.get_meta()
        name = md5(str.encode(' '.join([m['name'] for m in meta]), 'utf-8')).hexdigest()
        name += '.json'
        name = os.path.join(self.root, name)

        if os.path.exists(name):
            self.base_meta = self._load(name)
            self._check(meta)
        else:
            self._save(meta, name)

    def _save(self, meta, name) -> None:
        self.mh.write(name, meta)
        print(f'Saved as {name}!')

    def _load(self, name) -> dict:
        return self.mh.read(name)

    def _check(self, query_meta):
        diff = DeepDiff(self.base_meta, query_meta, verbose_level=2)
        if len(diff):
            print(diff.pretty())
            raise DataValidationException(diff)
        else:
            print('OK!')
