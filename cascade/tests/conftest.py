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
import random
import shutil
import numpy as np
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Wrapper, Iterator
from cascade.models import Model, ModelRepo


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


class EmptyModel(DummyModel):
   def __init__(self):
      pass


@pytest.fixture(params=[
        [1, 2, 3, 4, 5],
        [0],
        [0, 0, 0, 0],
        [-i for i in range(0, 100)]
   ])
def number_dataset(request):
   return Wrapper(request.param)


@pytest.fixture(params=[
        [1, 2, 3, 4, 5],
        [0],
        [0, 0, 0, 0],
        [-i for i in range(100, 0)]
   ])
def number_iterator(request):
   return Iterator(request.param)


@pytest.fixture(params=[
   {'a': 0},
   {'b': 1},
   {'a': 0, 'b': 'alala'},
   {'c': np.array([1, 2]), 'd': {'a': 0}}])
def dummy_model(request):
   return DummyModel(**request.param)


@pytest.fixture
def empty_model():
   return EmptyModel()


@pytest.fixture
def model_repo(tmp_path):
    repo = ModelRepo(str(tmp_path), lines=[
        dict(
            name=str(num),
            cls=DummyModel) for num in range(10)
        ])
    yield repo
