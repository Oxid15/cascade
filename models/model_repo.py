import os
import datetime
import json
from json import JSONEncoder
from typing import Any

from .model import Model


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        return super(DateTimeEncoder, self).default(obj)


class ModelRepo:
    def __init__(self, folder):
        self.root = folder
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
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
        with open(os.path.join(self.root, f'{len(self.models):0>5d}.json'), 'w') as json_meta:
            enc = DateTimeEncoder()
            json.dump(enc.encode(self.models[idx]['meta']), json_meta)
