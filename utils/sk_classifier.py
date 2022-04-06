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

import pickle
from sklearn.pipeline import Pipeline

from ..models import Model


class SkClassifier(Model):
    def __init__(self, name=None, blocks=[]):
        super().__init__()
        self.name = name
        if len(blocks):
            self.pipeline = self.construct_pipeline(blocks)

    def construct_pipeline(self, blocks):
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, x, y):
        self.pipeline.fit(x, y)

    def predict(self, x):
        return self.pipeline.predict(x)

    def evaluate(self, x, y, metrics_dict):
        preds = self.predict(x)
        self.metrics.update({key: metrics_dict[key](preds, y) for key in metrics_dict})

    def load(self, path_w_ext):
        with open(path_w_ext, 'rb') as f:
            self.pipeline = pickle.load(f)

    def save(self, path_wo_ext):
        with open(f'{path_wo_ext}.pkl', 'wb') as f:
            pickle.dump(self.pipeline, f)

    def get_meta(self):
        meta = super().get_meta()
        meta.update({
            'name': self.name if self.name is not None else None,
            'pipeline': repr(self.pipeline)
        })
        return meta
