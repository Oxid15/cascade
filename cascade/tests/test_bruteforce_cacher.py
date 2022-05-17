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
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.number_dataset import NumberDataset
from cascade.tests.number_iterator import NumberIterator
from cascade.data import BruteforceCacher


class TestBruteforceCacher(TestCase):
    def test(self):
        ds = NumberDataset([1, 2, 3, 4, 5])
        ds = BruteforceCacher(ds)
        self.assertEqual([1, 2, 3, 4, 5], [item for item in ds])

        ds = NumberIterator(6)
        ds = BruteforceCacher(ds)
        self.assertEqual([0, 1, 2, 3, 4, 5], [item for item in ds])

    def test_meta(self):
        ds = NumberDataset([1, 2, 3, 4, 5])
        ds = BruteforceCacher(ds)
        meta = ds.get_meta()

        self.assertEqual(len(meta), 2)


if __name__ == '__main__':
    unittest.main()
