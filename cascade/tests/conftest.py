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

import datetime
import os
import sys
from typing import Any

import numpy as np
import pendulum
import pytest
from dateutil import tz

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import (ApplyModifier, BruteforceCacher, Composer,
                          Concatenator, CyclicSampler, Dataset, Iterator,
                          RandomSampler, RangeSampler, SequentialCacher,
                          Wrapper)
from cascade.models import BasicModel, ModelLine, ModelRepo


class DummyModel(BasicModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = "model"

    def fit(self, *args, **kwargs):
        pass

    def predict(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs):
        self.add_metric("acc", np.random.random())

    def save_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        with open(os.path.join(path, "model"), "w") as f:
            f.write(self.model)


class EmptyModel(DummyModel):
    def __init__(self):
        pass


class OnesModel(BasicModel):
    def predict(self, x, *args, **kwargs):
        return np.array([1 for _ in range(len(x))])

    def fit(self, x, y, *args, **kwargs) -> None:
        pass


def f(x: int) -> int:
    return 2 * x


@pytest.fixture
def tmp_path_str(tmp_path) -> str:
    return str(tmp_path)


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
        SequentialCacher(Wrapper([0, 1, 2, 3])),
    ]
)
def dataset(request) -> Dataset:
    return request.param


@pytest.fixture(
    params=[[1, 2, 3, 4, 5], [0], [0, 0, 0, 0], [-i for i in range(0, 100)]]
)
def number_dataset(request):
    return Wrapper(request.param)


@pytest.fixture(
    params=[[1, 2, 3, 4, 5], [0], [0, 0, 0, 0], [-i for i in range(100, 0)]]
)
def number_iterator(request):
    return Iterator(request.param)


@pytest.fixture(
    params=[
        {"a": 0},
        {"b": 1},
        {"a": 0, "b": "alala"},
        {"c": np.array([1, 2]), "d": {"a": 0}},
        {"e": datetime.datetime(2022, 7, 8, 16, 4, 3, 5, tz.gettz("Europe / Moscow"))},
        {"f": pendulum.datetime(2022, 7, 8, 16, 4, 3, 5, "Europe/Moscow")},
        {"g": {}},
        {"h": []},
        {"i": None},
    ]
)
def dummy_model(request):
    return DummyModel(**request.param)


@pytest.fixture
def empty_model():
    return EmptyModel()


@pytest.fixture(
    params=[
        {"model_cls": DummyModel, "meta_fmt": ".json"},
        {"model_cls": DummyModel, "meta_fmt": ".yml"},
    ]
)
def model_line(request, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("line-", numbered=True)
    tmp_path = os.path.join(tmp_path, "line")
    line = ModelLine(str(tmp_path), **request.param)
    return line


@pytest.fixture
def ones_model():
    return OnesModel()


@pytest.fixture
def model_repo(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("repo-", numbered=True)
    tmp_path = os.path.join(tmp_path, "repo")
    repo = ModelRepo(
        str(tmp_path),
        lines=[dict(name=str(num), model_cls=DummyModel) for num in range(10)],
    )
    return repo


@pytest.fixture(params=[{"repo_or_line": True}, {"repo_or_line": False}])
def repo_or_line(request, model_repo, model_line):
    if request.param["repo_or_line"]:
        return model_repo
    else:
        return model_line
