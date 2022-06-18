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
from cascade.data import Concatenator


class TestConcatenator(TestCase):
    def test_meta(self):
        n1 = NumberDataset([0, 1])
        n2 = NumberDataset([2, 3, 4, 5])

        c = Concatenator([n1, n2], meta_prefix={'num': 1})
        self.assertEqual(c.get_meta()[0]['num'], 1)

    def test_concatenation(self):
        n1 = NumberDataset([0, 1])
        n2 = NumberDataset([2, 3, 4, 5])
        n3 = NumberDataset([6, 7, 8])
        n4 = NumberDataset([1])

        c = Concatenator([n1, n2, n4, n3, n4])
        self.assertEqual([c[i] for i in range(len(c))],
                         [0, 1, 2, 3, 4, 5, 1, 6, 7, 8, 1])


if __name__ == '__main__':
    unittest.main()
