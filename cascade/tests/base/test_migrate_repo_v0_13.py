"""
Copyright 2022-2025 Ilia Moiseev

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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler
from cascade.base.utils import migrate_repo_v0_13
from cascade.models import Model
from cascade.repos import Repo


class OldStyleModel(Model):
    def get_meta(self):
        meta = super().get_meta()
        if "cascade_version" in meta[0]:
            del meta[0]["cascade_version"]
        return meta


def test_scalars_only(tmp_path_str):
    repo = Repo(tmp_path_str)
    line = repo.add_line()

    model = OldStyleModel()
    # Make old-style metrics by overwriting with dict
    model.metrics = {
        "acc": 0.55
    }

    line.save(model, only_meta=True)

    migrate_repo_v0_13(tmp_path_str)

    model_path = os.path.join(tmp_path_str, "00000", "00000")
    meta = MetaHandler.read_dir(model_path)
    assert "metrics" in meta[0]
    assert isinstance(meta[0]["metrics"], list)
    assert len(meta[0]["metrics"]) == 1
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == 0.55
    assert "old_metrics" not in meta[0]
    assert "cascade_version" in meta[0]

    meta_line = MetaHandler.read_dir(os.path.join(tmp_path_str, "00000"))
    assert "cascade_version" in meta_line[0]

    meta_repo = MetaHandler.read_dir(tmp_path_str)
    assert "cascade_version" in meta_repo[0]


def test_complex_metrics(tmp_path_str):
    repo = Repo(tmp_path_str)
    line = repo.add_line()

    model = OldStyleModel()
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

    migrate_repo_v0_13(tmp_path_str)

    model_path = os.path.join(tmp_path_str, "00000", "00000")
    meta = MetaHandler.read_dir(model_path)
    assert "metrics" in meta[0]
    assert isinstance(meta[0]["metrics"], list)
    assert len(meta[0]["metrics"]) == 1
    assert meta[0]["metrics"][0]["name"] == "acc"
    assert meta[0]["metrics"][0]["value"] == 0.55
    assert "old_metrics" in meta[0]
    assert meta[0]["old_metrics"] == {"complex": model.metrics["complex"]}

    meta_line = MetaHandler.read_dir(os.path.join(tmp_path_str, "00000"))
    assert "cascade_version" in meta_line[0]

    meta_repo = MetaHandler.read_dir(tmp_path_str)
    assert "cascade_version" in meta_repo[0]


def test_idempotency(tmp_path_str):
    repo = Repo(tmp_path_str)
    line = repo.add_line()

    model = OldStyleModel()
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

    # Do the migration twice
    migrate_repo_v0_13(tmp_path_str)
    migrate_repo_v0_13(tmp_path_str)

    model_path = os.path.join(tmp_path_str, "00000", "00000")
    meta = MetaHandler.read_dir(model_path)

    assert meta[0]["metrics"][0]["name"] == "acc"
