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

from cascade.data import RandomSampler
from cascade.tests.number_dataset import NumberDataset


class TestRandomSampler(TestCase):
    def test(self):
        ds = NumberDataset([0, 1, 2, 3, 4])
        ds = RandomSampler(ds)

        self.assertNotEqual(
            [ds[i] for i in range(len(ds))],
            [0, 1, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()
