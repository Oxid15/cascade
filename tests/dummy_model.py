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
import sys
import numpy as np

sys.path.append(os.path.abspath('../..'))
from cascade.models import Model


class DummyModel(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = b'model'

    def fit(self, *args, **kwargs):
        pass

    def predict(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs):
        self.metrics.update({'acc': np.random.random()})

    def load(self, path):
        if os.path.splitext(path)[-1] != '.bin':
            path += '.bin'
        with open(path, 'rb') as f:
            self.model = str(f.read())

    def save(self, path):
        if os.path.splitext(path)[-1] != '.bin':
            path += '.bin'
        with open(path, 'wb') as f:
            f.write(b'model')
