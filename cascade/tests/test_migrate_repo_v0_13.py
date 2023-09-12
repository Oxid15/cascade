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

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base.utils import migrate_repo_v0_13
from cascade.base import MetaHandler
from cascade.models import ModelRepo, Model


def test_scalars_only(tmp_path):
    tmp_path = str(tmp_path)

    repo = ModelRepo(tmp_path)
    line = repo.add_line()

    model = Model()
    # Make old-style metrics by overwriting with dict
    model.metrics = {
        "acc": 0.55
    }

    line.save(model, only_meta=True)

    migrate_repo_v0_13(tmp_path)

    model_path = os.path.join(tmp_path, "00000", "00000")
    meta = MetaHandler.read_dir(model_path)
    assert "metrics" in meta[0]
    assert isinstance(meta[0]["metrics"], list)
    assert len(meta[0]["metrics"]) == 1
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == 0.55
    assert "old_metrics" not in meta[0]


def test_complex_metrics(tmp_path):
    tmp_path = str(tmp_path)

    repo = ModelRepo(tmp_path)
    line = repo.add_line()

    model = Model()
    # Make old-style metrics by overwriting with dict
    model.metrics = {
        "acc": 0.55,
        "complex": {
            "metric_1": 1,
            "metric_2": 2,
            "metric_arr": [0, 1, 2]
        }
    }

    line.save(model, only_meta=True)

    migrate_repo_v0_13(tmp_path)

    model_path = os.path.join(tmp_path, "00000", "00000")
    meta = MetaHandler.read_dir(model_path)
    assert "metrics" in meta[0]
    assert isinstance(meta[0]["metrics"], list)
    assert len(meta[0]["metrics"]) == 1
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == 0.55
    assert "old_metrics" in meta[0]
    assert meta[0]["old_metrics"] == {"complex": model.metrics["complex"]}
