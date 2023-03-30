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

from cascade.models.trainer import BasicTrainer

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.conftest import DummyModel
from cascade.models import Trainer, ModelRepo
from cascade.data import Wrapper


def test_base(tmp_path, model_repo):
    t = Trainer(str(tmp_path))
    meta = t.get_meta()

    assert len(meta) == 1
    assert 'repo' in meta[0]
    assert 'metrics' in meta[0]

    t = Trainer(model_repo)
    meta = t.get_meta()

    assert len(meta) == 1
    assert 'repo' in meta[0]
    assert 'metrics' in meta[0]


def test_basic_trainer(tmp_path):
    repo = ModelRepo(str(tmp_path))
    t = BasicTrainer(repo)

    model = DummyModel()

    t.train(
        model,
        Wrapper([0, 1, 2, 3, 4]),
        Wrapper([0, 1, 2, 3, 4]),
        epochs=5
    )

    assert len(repo) == 1
    assert len(repo['00000']) == 5
    assert len(t.metrics) == 5
