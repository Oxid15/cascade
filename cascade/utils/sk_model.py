"""
Copyright 2022 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import glob
from hashlib import md5
import pickle
from sklearn.pipeline import Pipeline

from ..meta import MetaHandler
from ..models import Model


class SkModel(Model):
    def __init__(self, name=None, blocks=[], **kwargs):
        super().__init__(name=name, **kwargs)
        self.name = name
        if len(blocks):
            self.pipeline = self._construct_pipeline(blocks)

    def _construct_pipeline(self, blocks):
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, x, y):
        self.pipeline.fit(x, y)

    def predict(self, x):
        return self.pipeline.predict(x)

    def evaluate(self, x, y, metrics_dict):
        preds = self.predict(x)
        self.metrics.update({key: metrics_dict[key](preds, y) for key in metrics_dict})

    def _check_model_hash(self, meta, path_w_ext):
        with open(path_w_ext, 'rb') as f:
            file_hash = md5(f.read()).hexdigest()
        if file_hash == meta['md5sum']:
            return
        else:
            raise RuntimeError(f'.pkl model hash check failed\n \
                 it may be that model\'s .pkl file was corrupted\n \
                 hash from meta: {meta["md5sum"]}\n \
                 hash from .pkl: {file_hash}')

    def load(self, path):
        if os.path.splitext(path)[-1] != '.pkl':
            path += '.pkl'
        root = os.path.dirname(path)
        names = glob.glob(os.path.join(f'{root}', 'meta.json'))
        if len(names):
            meta = MetaHandler().read(names[0])
            if 'md5sum' in meta:
                self._check_model_hash(meta, path)

        with open(path, 'rb') as f:
            self.pipeline = pickle.load(f)

    def save(self, path):
        if os.path.splitext(path)[-1] != '.pkl':
            path += '.pkl'
        with open(f'{path}', 'wb') as f:
            pickle.dump(self.pipeline, f)

    def get_meta(self):
        meta = super().get_meta()
        meta[0].update({
            'name': self.name if self.name is not None else None,
            'pipeline': repr(self.pipeline)
        })
        return meta
