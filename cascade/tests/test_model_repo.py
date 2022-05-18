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

from cascade.models import ModelRepo
from cascade.tests.dummy_model import DummyModel


class TestModelRepo(TestCase):
    def test_repo(self):
        repo = ModelRepo('./test_models')
        repo.add_line('dummy_1', DummyModel)
        repo.add_line('00001', DummyModel)

        self.assertTrue(os.path.exists('./test_models/dummy_1'))
        self.assertTrue(os.path.exists('./test_models/00001'))

        shutil.rmtree('./test_models')
        self.assertEqual(2, len(repo))

    def test_overwrite(self):
        # If no overwrite repo will have 4 models
        repo = ModelRepo('./test_overwrite', overwrite=True)
        repo.add_line('vgg16', DummyModel)
        repo.add_line('resnet', DummyModel)

        repo = ModelRepo('./test_overwrite', overwrite=True)
        repo.add_line('densenet', DummyModel)
        repo.add_line('efficientnet', DummyModel)

        shutil.rmtree('./test_overwrite')
        self.assertEqual(2, len(repo))

    def test_add_line(self):
        repo = ModelRepo('./test_overwrite', overwrite=True)
        with self.assertRaises(AssertionError):
            repo.add_line(DummyModel, 'vgg16')  # wrong argument order

    def test_reusage(self):
        repo = ModelRepo('./test_reusage')

        repo.add_line('vgg16', DummyModel)

        model = DummyModel()
        repo['vgg16'].save(model)

        # some time...

        repo = ModelRepo('./test_reusage')
        repo.add_line('vgg16', DummyModel)

        shutil.rmtree('./test_reusage')
        self.assertEqual(len(repo['vgg16']), 1)

    def test_reusage_init_alias(self):
        repo = ModelRepo('./test_reusage_init_alias')

        repo.add_line('vgg16', DummyModel)

        model = DummyModel()
        repo['vgg16'].save(model)

        # some time...

        repo = ModelRepo('./test_reusage_init_alias',
                         lines=[dict(
                             name='vgg16',
                             cls=DummyModel
                         )])

        shutil.rmtree('./test_reusage_init_alias')
        self.assertEqual(len(repo['vgg16']), 1)

    def test_meta(self):
        repo = ModelRepo('./test_repo_meta')
        repo.add_line('00000', DummyModel)
        repo.add_line('00001', DummyModel)

        shutil.rmtree('./test_repo_meta')  # Cleanup

        meta = repo.get_meta()
        self.assertEqual(meta[0]['len'], 2)


if __name__ == '__main__':
    unittest.main()
