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
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.conftest import DummyModel
from cascade.models import ModelRepo
from cascade.meta import MetricViewer


def test(model_repo, dummy_model):
    m = dummy_model
    m.evaluate()
    model_repo['0'].save(m)

    mtv = MetricViewer(model_repo)
    t = mtv.table

    for item in ['line', 'num', 'created_at', 'saved', 'acc']:
        assert item in list(t.columns)


def test_show_table(model_repo, dummy_model):
    for _ in range(len(model_repo)):
        m = dummy_model
        m.evaluate()
        model_repo['0'].save(m)

    mtv = MetricViewer(model_repo)
    mtv.plot_table(show=True)


@pytest.mark.skip
def test_serve(model_repo):
    mtv = MetricViewer(model_repo)
    mtv.serve()


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_missing_model_meta(tmp_path, dummy_model, ext):
    model_repo = ModelRepo(str(tmp_path))
    model_repo.add_line('test', model_cls=DummyModel, meta_fmt=ext)
    dummy_model.evaluate()
    model_repo['test'].save(dummy_model)
    model_repo['test'].save(dummy_model)

    os.remove(os.path.join(tmp_path, 'test', '00000', 'meta' + ext))

    mv = MetricViewer(model_repo)
    mv.plot_table()
