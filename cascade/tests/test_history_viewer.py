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

from cascade.tests.conftest import EmptyModel, DummyModel
from cascade.models import ModelRepo
from cascade.meta import HistoryViewer


def test_run(model_repo, dummy_model):
    dummy_model.evaluate()
    model_repo['0'].save(dummy_model)

    hv = HistoryViewer(model_repo)
    hv.plot('acc')


def test_no_metric(model_repo, dummy_model):
    model_repo['0'].save(dummy_model)

    hv = HistoryViewer(model_repo)
    with pytest.raises(AssertionError):
        hv.plot('acc')


def test_empty_model(model_repo, empty_model):
    model_repo.add_line('test', EmptyModel)
    empty_model.metrics = {'acc': 0.9}
    model_repo['test'].save(empty_model)

    hv = HistoryViewer(model_repo)
    hv.plot('acc')


def test_many_lines(model_repo, dummy_model):
    model0 = dummy_model
    model0.evaluate()

    model1 = dummy_model
    model1.evaluate()

    model_repo['0'].save(model0)
    model_repo['1'].save(model1)

    hv = HistoryViewer(model_repo)
    hv.plot('acc')


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

    hv = HistoryViewer(model_repo)
    hv.plot('acc')
