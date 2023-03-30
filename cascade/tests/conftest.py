"""
Copyright 2022-2023 Ilia Moiseev

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
import datetime
import pendulum
from dateutil import tz
import numpy as np
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Dataset, Wrapper, Iterator, ApplyModifier, \
    BruteforceCacher, Composer, Concatenator, CyclicSampler, \
    RandomSampler, RangeSampler, SequentialCacher
from cascade.models import Model, ModelLine, ModelRepo, BasicModel


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


class OnesModel(BasicModel):
    def predict(self, x, *args, **kwargs):
        return np.array([1 for _ in range(len(x))])

    def load(self, filepath) -> None:
        pass

    def save(self, filepath) -> None:
        pass

    def fit(self, x, y, *args, **kwargs) -> None:
        pass


def f(x: int) -> int:
    return 2 * x


@pytest.fixture(
    params=[
        Iterator([0]),
        Wrapper([0]),
        ApplyModifier(Wrapper([0, 1, 2]), f),
        BruteforceCacher(Wrapper([0, 2])),
        Composer([Wrapper([0]), Wrapper([1])]),
        Concatenator([Wrapper([0]), Wrapper([1])]),
        CyclicSampler(Wrapper([0]), 1),
        RandomSampler(Wrapper([1, 2, 3]), 2),
        RangeSampler(Wrapper([0, 1, 2, 3]), 0, 3, 1),
        SequentialCacher(Wrapper([0, 1, 2, 3]))
    ]
)
def dataset(request) -> Dataset:
    return request.param


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
    {'c': np.array([1, 2]), 'd': {'a': 0}},
    {'e': datetime.datetime(2022, 7, 8, 16, 4, 3, 5, tz.gettz('Europe / Moscow'))},
    {'f': pendulum.datetime(2022, 7, 8, 16, 4, 3, 5, 'Europe/Moscow')},
    {'g': {}},
    {'h': []},
    {'i': None}
])
def dummy_model(request):
    return DummyModel(**request.param)


@pytest.fixture
def empty_model():
    return EmptyModel()


@pytest.fixture(params=[
    {
        'model_cls': DummyModel,
        'meta_fmt': '.json'
    },
    {
        'model_cls': DummyModel,
        'meta_fmt': '.yml'
    }
])
def model_line(request, tmp_path):
    line = ModelLine(str(tmp_path), **request.param)
    return line


@pytest.fixture
def ones_model():
    return OnesModel()


@pytest.fixture
def model_repo(tmp_path):
    repo = ModelRepo(str(tmp_path), lines=[
        dict(
            name=str(num),
            model_cls=DummyModel) for num in range(10)
    ])
    return repo
