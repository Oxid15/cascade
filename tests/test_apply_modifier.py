import os
import sys
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.number_dataset import NumberDataset
from cascade.data import ApplyModifier


class TestApplyModifier(TestCase):
    def test(self):
        ds = NumberDataset([1, 2, 3, 4, 5])
        ds = ApplyModifier(ds, lambda x: x * 2)
        self.assertEqual([2, 4, 6, 8, 10], [item for item in ds])


if __name__ == '__main__':
    unittest.main()
