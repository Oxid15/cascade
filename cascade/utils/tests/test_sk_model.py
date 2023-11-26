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
import shutil
import sys

import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))


import cascade as csd
from cascade.utils.sklearn import SkModel


# Skipped until hash check can be returned
@pytest.mark.skip
@pytest.mark.parametrize("ext", [".json", ".yml"])
def test_hash_check(tmp_path_str, ext):
    repo = csd.models.ModelRepo(tmp_path_str, overwrite=True, meta_fmt=ext)

    tree = SkModel(blocks=[DecisionTreeClassifier()])

    forest = SkModel(blocks=[RandomForestClassifier()])

    line = repo.add_line("tree", SkModel)
    line.save(tree)
    line.save(forest)

    # This should pass
    tree.load(os.path.join(tmp_path_str, "tree", "00000", "model"))

    # This should fail
    shutil.move(
        os.path.join(tmp_path_str, "tree", "00001", "model.pkl"),
        os.path.join(tmp_path_str, "tree", "00000", "model.pkl"),
    )

    with pytest.raises(RuntimeError):
        tree.load(os.path.join(tmp_path_str, "tree", "00000", "model"))


def test_save_load(tmp_path_str):

    model = SkModel(blocks=[RandomForestClassifier(n_estimators=2)], custom_param=42)
    model.save(tmp_path_str)

    assert model._pipeline

    model = SkModel.load(tmp_path_str)

    assert model.params.get("custom_param") == 42


def test_model_artifacts(tmp_path_str):

    model = SkModel(blocks=[RandomForestClassifier(n_estimators=2)], custom_param=42)
    model.save_artifact(tmp_path_str)

    assert os.path.exists(os.path.join(tmp_path_str, "pipeline.pkl"))
    assert not os.path.exists(os.path.join(tmp_path_str, "model.pkl"))

    model = SkModel()
    model.load_artifact(tmp_path_str)
    assert model._pipeline[0].n_estimators == 2
