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
import shutil
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.dummy_model import DummyModel
from cascade.models import ModelRepo
from cascade.meta import HistoryViewer


class TestHistoryViewer(TestCase):
    def simple_test(self):
        repo = ModelRepo('./test_history_viewer')

        line0 = repo.add_line('0', DummyModel)

        model = DummyModel()
        model.evaluate()

        line0.save(model)

        hv = HistoryViewer(repo)
        hv.plot('acc')
        shutil.rmtree('./test_history_viewer')


if __name__ == '__main__':
    unittest.main()
