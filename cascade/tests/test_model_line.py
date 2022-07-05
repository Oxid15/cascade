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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.conftest import DummyModel
from cascade.models.model_repo import ModelLine


def test_save_load():
    line = ModelLine('./line', DummyModel)
    m = DummyModel()
    line.save(m)
    model = line[0]

    assert(len(line) == 1)
    assert(model.model == "b'model'")


def test_meta():
    line = ModelLine('line_meta', DummyModel)
    m = DummyModel()
    line.save(m)
    meta = line.get_meta()

    assert(meta[0]['model_cls'] == repr(DummyModel))
    assert(meta[0]['len'] == 1)
