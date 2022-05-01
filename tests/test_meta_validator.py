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
import json
import shutil
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.number_dataset import NumberDataset
from cascade.meta import MetaValidator, DataValidationException


class TestMetaValidator(TestCase):
    def pipeline_run(self, arr):
        ds = NumberDataset(arr)
        ds = MetaValidator(ds)

    def test_true(self):
        self.pipeline_run([1, 2, 3, 4, 5])
        self.pipeline_run([1, 2, 3, 4, 5])

    def test_raise(self):
        self.pipeline_run([1, 2, 3, 4, 5])
        with self.assertRaises(DataValidationException):
            self.pipeline_run([1, 2, 3, 4, 5, 6])


if __name__ == '__main__':
    unittest.main()
