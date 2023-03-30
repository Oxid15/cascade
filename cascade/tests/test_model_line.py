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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.conftest import DummyModel


def test_save_load(model_line, dummy_model):
    model_line.save(dummy_model)
    model = model_line[0]

    assert len(model_line) == 1
    assert model.model == "b'model'"


def test_meta(model_line, dummy_model):
    model_line.save(dummy_model)
    meta = model_line.get_meta()

    assert meta[0]['model_cls'] == repr(DummyModel)
    assert meta[0]['len'] == 1
