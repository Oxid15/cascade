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
import unittest
import shutil
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.dummy_model import DummyModel
from cascade.models.model_repo import ModelLine


class TestModelLine(TestCase):
    def test_save_load(self):
        line = ModelLine('./line', DummyModel)

        m = DummyModel()

        line.save(m)

        model = line[0]

        shutil.rmtree('./line')  # Cleanup

        self.assertEqual(len(line), 1)
        self.assertTrue(model.model == "b'model'")

    def test_meta(self):
        line = ModelLine('line_meta', DummyModel)

        m = DummyModel()

        line.save(m)

        shutil.rmtree('./line_meta')  # Cleanup

        meta = line.get_meta()
        self.assertEqual(meta[0]['model_cls'], repr(DummyModel))
        self.assertEqual(meta[0]['len'], 1)


if __name__ == '__main__':
    unittest.main()
