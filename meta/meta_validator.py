import os
from hashlib import md5
from deepdiff import DeepDiff
from . import Validator, MetaHandler, DataValidationException


class MetaValidator(Validator):
    def __init__(self, dataset, root='./'):
        super().__init__(dataset, lambda x: True)
        self.mh = MetaHandler()
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

    def _save(self, meta, name):
        self.mh.write(name, meta)
        print(f'Saved as {name}!')

    def _load(self, name):
        return self.mh.read(name)

    def _check(self, query_meta):
        diff = DeepDiff(self.base_meta, query_meta, verbose_level=2)
        if len(diff):
            print(diff.pretty())
            raise DataValidationException(diff)
        else:
            print('OK!')
