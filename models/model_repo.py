import os
import datetime
import json
import glob
from json import JSONEncoder
from hashlib import md5

import numpy as np

from .model import Model


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        
        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}
        
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
    
        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return super(CustomEncoder, self).default(obj)


class ModelRepo:
    def __init__(self, folder, model_csl=Model):
        self.root = folder
        self.model_cls = model_csl
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.lines = {name: ModelLine(os.path.join(self.root, name), model_csl=model_csl)
                          for name in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, name))}
            print(f'Found {len(self.lines)}' + ' lines')
        else:
            os.mkdir(self.root)
            self.lines = dict()

    def _new_line(self, name=None):
        if name is None:
            name = f'{len(self.lines):05d}'
        else:
            name = str(name)

        folder = os.path.join(self.root, name)
        line = ModelLine(folder, self.model_cls)
        self.lines[name] = line
        return line

    def __getitem__(self, key):
        if key in self.lines:
            return self.lines[key]
        else:
            return self._new_line(key)

    def __len__(self):
        return len(self.lines)


class ModelLine:
    def __init__(self, folder, model_csl=Model):
        self.model_csl = model_csl
        self.root = folder
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.models = {i: name for i, name in enumerate(os.listdir(self.root)) if not name.endswith('.json')}
            print(f'Found {len(self.models)}' + ' models')
        else:
            os.mkdir(self.root)
            self.models = {}

    def __getitem__(self, name) -> Model:
        model = self.model_csl()
        model.load(os.path.join(self.root, self.models[name]))
        return model

    def __len__(self):
        return len(self.models)

    def save(self, model: Model) -> None:
        idx = len(self.models)
        name = os.path.join(self.root, f'{idx:0>5d}')
        self.models[idx] = name
        model.save(name)

        exact_filename = glob.glob(f'{name}*')[0]
        with open(exact_filename, 'rb') as f:
            md5sum = md5(f.read()).hexdigest()

        meta = {
            'md5sum': md5sum,
            'created_at': model.created_at,
            'saved_at': datetime.datetime.now(),
            'metrics': model.metrics
        }

        with open(os.path.join(self.root, f'{idx:0>5d}.json'), 'w') as json_meta:
            enc = CustomEncoder()
            json.dump(enc.encode(meta), json_meta)
