import os
import datetime
import json

from .model import Model


class ModelRepo:
    def __init__(self, folder):
        assert os.path.isdir(folder)

        self.root = folder
        if os.path.exists(self.root):
            raise NotImplementedError('Folder startup is not impl')
        else:
            os.mkdir(self.root)
            self.models = {}

    def save(self, model: Model):
        idx = len(self.models)
        self.models[idx] = {}
        self.models[idx]['model'] = model
        self.models[idx]['meta'] = {
            'created_at': model.created_at,
            'saved_at': datetime.datetime.now()
        }
        model.save(os.path.join(self.root, f'{len(self.models):0>5d}'))
        with open(os.path.join(self.root, f'{len(self.models):0>5d}.json')) as json_meta:
            json.dump(self.models[idx]['meta'], json_meta)
