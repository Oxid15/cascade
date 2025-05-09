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

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import HistoryViewer
from cascade.repos import Repo
from cascade.tests.conftest import DummyModel, EmptyModel


def test_run(repo_or_line, dummy_model):
    dummy_model.evaluate()
    if isinstance(repo_or_line, Repo):
        repo_or_line["0"].save(dummy_model)
    else:
        repo_or_line.save(dummy_model)

    hv = HistoryViewer(repo_or_line)
    hv.plot("acc")


def test_no_metric(repo_or_line, dummy_model):
    if isinstance(repo_or_line, Repo):
        repo_or_line["0"].save(dummy_model)
    else:
        repo_or_line.save(dummy_model)

    hv = HistoryViewer(repo_or_line)
    with pytest.raises(AssertionError):
        hv.plot("acc")


def test_empty_model(repo, empty_model):
    repo.add_line("test", model_cls=EmptyModel)
    empty_model.add_metric("acc", 0.9)
    repo["test"].save(empty_model)

    hv = HistoryViewer(repo)
    hv.plot("acc")


def test_many_lines(repo, dummy_model):
    model0 = dummy_model
    model0.evaluate()

    model1 = dummy_model
    model1.evaluate()

    repo["0"].save(model0)
    repo["1"].save(model1)

    hv = HistoryViewer(repo)
    hv.plot("acc")


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_missing_model_meta(tmp_path_str, dummy_model, ext):
    model_repo = Repo(tmp_path_str)
    model_repo.add_line("test", model_cls=DummyModel, meta_fmt=ext)
    dummy_model.evaluate()
    model_repo["test"].save(dummy_model)
    model_repo["test"].save(dummy_model)

    os.remove(os.path.join(tmp_path_str, "test", "00000", "meta" + ext))

    hv = HistoryViewer(model_repo)
    hv.plot("acc")
