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
import numpy as np
import shutil
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.dummy_model import DummyModel
from cascade.models import ModelRepo
from cascade.meta import HistoryViewer


class TestHistoryViewer(TestCase):
    def test_run(self):
        repo = ModelRepo('./test_hv')

        line0 = repo.add_line('0', DummyModel)

        model = DummyModel()
        model.evaluate()

        line0.save(model)

        hv = HistoryViewer(repo)
        hv.plot('acc')
        shutil.rmtree('./test_hv')

    def test_no_metric(self):
        repo = ModelRepo('./test_hv_no_metric')

        line0 = repo.add_line('0', DummyModel)

        model = DummyModel()
        # model.evaluate()

        line0.save(model)

        hv = HistoryViewer(repo)
        with self.assertRaises(AssertionError):
            hv.plot('acc')

        shutil.rmtree('./test_hv_no_metric')

    def test_params(self):
        repo = ModelRepo('./test_hv_params')

        line0 = repo.add_line('0', DummyModel)

        model0 = DummyModel(a=0)
        model0.evaluate()

        model1 = DummyModel(a=0, b=0)
        model1.evaluate()

        line0.save(model0)
        line0.save(model1)

        hv = HistoryViewer(repo)
        hv.plot('acc')

        shutil.rmtree('./test_hv_params')

    def test_empty_model(self):
        class EmptyModel(DummyModel):
            def __init__(self):
                self.metrics = {'acc': np.random.random()}

        repo = ModelRepo('./test_empty')

        line0 = repo.add_line('0', EmptyModel)

        model0 = EmptyModel()
        model1 = EmptyModel()

        line0.save(model0)
        line0.save(model1)

        hv = HistoryViewer(repo)
        hv.plot('acc')

        shutil.rmtree('./test_empty')

    def test_many_lines(self):
        repo = ModelRepo('./test_many_lines', lines=[
            dict(
                name=str(num),
                cls=DummyModel) for num in range(50)
            ])

        model0 = DummyModel(a=0)
        model0.evaluate()

        model1 = DummyModel(a=0, b=0)
        model1.evaluate()

        repo['0'].save(model0)
        repo['1'].save(model1)

        hv = HistoryViewer(repo)
        hv.plot('acc')

        shutil.rmtree('./test_many_lines')


if __name__ == '__main__':
    unittest.main()
