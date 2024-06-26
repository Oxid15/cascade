"""
Copyright 2022-2024 Ilia Moiseev

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
from typing import NoReturn

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler
from cascade.data import Wrapper
from cascade.models import BasicTrainer, ModelRepo, Trainer
from cascade.tests.conftest import DummyModel


class AlwaysFailingModel(DummyModel):
    def fit(self, *args, **kwargs) -> NoReturn:
        raise RuntimeError()

    def evaluate(self, *args, **kwargs) -> NoReturn:
        raise RuntimeError()


def test_base(tmp_path_str, model_repo):
    t = Trainer(tmp_path_str)
    meta = t.get_meta()

    assert len(meta) == 1
    assert "repo" in meta[0]
    assert "metrics" in meta[0]

    t = Trainer(model_repo)
    meta = t.get_meta()

    assert len(meta) == 1
    assert "repo" in meta[0]
    assert "metrics" in meta[0]


def test_basic_trainer(tmp_path_str):
    repo = ModelRepo(tmp_path_str)
    t = BasicTrainer(repo)

    model = DummyModel()

    t.train(model, Wrapper([0, 1, 2, 3, 4]), Wrapper([0, 1, 2, 3, 4]), epochs=5)

    assert len(repo) == 1
    assert len(repo["00000"]) == 5
    assert len(t.metrics) == 5

    trainer_meta = t.get_meta()

    assert trainer_meta[0]["epochs"] == 5
    assert trainer_meta[0]["eval_strategy"] is None
    assert trainer_meta[0]["save_strategy"] is None

    line_meta = MetaHandler.read_dir(repo["00000"].get_root())
    assert len(line_meta[0]["links"]) == 3
    for link in line_meta[0]["links"]:
        if link["meta"][0].get("type") == "trainer":
            assert "epochs" in link["meta"][0]
            assert "eval_strategy" in link["meta"][0]
            assert "save_strategy" in link["meta"][0]
        elif link["meta"][0].get("type") == "dataset":
            assert link["meta"][0]["len"] == 5


def test_error_handling(tmp_path_str):
    repo = ModelRepo(tmp_path_str)
    t = BasicTrainer(repo)

    model = AlwaysFailingModel()

    t.train(model, Wrapper([0, 1, 2, 3, 4]), Wrapper([0, 1, 2, 3, 4]), epochs=5)

    assert len(repo) == 1
    assert len(repo["00000"]) == 1
    assert len(t.metrics) == 0
