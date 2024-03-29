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

from cascade.meta import MetricViewer
from cascade.models import ModelRepo
from cascade.tests.conftest import DummyModel


def test(repo_or_line, dummy_model):
    m = dummy_model
    m.evaluate()

    if isinstance(repo_or_line, ModelRepo):
        first = repo_or_line.get_line_names()[0]
        repo_or_line[first].save(m)
    else:
        repo_or_line.save(m)

    mtv = MetricViewer(repo_or_line)
    t = mtv.table

    for item in ["line", "num", "created_at", "saved", "acc"]:
        assert item in list(t.columns)


def test_show_table(model_repo, dummy_model):
    first = model_repo.get_line_names()[0]
    for _ in range(len(model_repo)):
        m = dummy_model
        m.evaluate()
        model_repo[first].save(m)

    mtv = MetricViewer(model_repo)
    mtv.plot_table(show=True)


@pytest.mark.skip
def test_serve(repo_or_line):
    mtv = MetricViewer(repo_or_line)
    mtv.serve()


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_missing_model_meta(tmp_path_str, dummy_model, ext):
    model_repo = ModelRepo(tmp_path_str, meta_fmt=ext)
    model_repo.add_line("test", model_cls=DummyModel)
    dummy_model.evaluate()
    model_repo["test"].save(dummy_model)
    model_repo["test"].save(dummy_model)

    os.remove(os.path.join(tmp_path_str, "test", "00000", "meta" + ext))

    mv = MetricViewer(model_repo)
    mv.plot_table()


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_get_best_by(tmp_path_str, ext):
    repo = ModelRepo(tmp_path_str, meta_fmt=ext, model_cls=DummyModel)
    line = repo.add_line("00001", model_cls=DummyModel)

    model = DummyModel()
    model.evaluate()
    line.save(model)

    model = DummyModel()
    line.save(model)

    mv = MetricViewer(repo)
    mv.get_best_by("acc")
