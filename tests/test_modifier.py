import os
import sys
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Modifier
from cascade.tests.number_dataset import NumberDataset


class TestModifier(TestCase):
    def test_iter(self):
        d = NumberDataset([1, 2, 3, 4, 5])
        m = Modifier(d)

        result1 = []
        for item in m:
            result1.append(item)

        result2 = []
        for item in m:
            result2.append(item)

        self.assertEqual([1, 2, 3, 4, 5], result1)
        self.assertEqual([1, 2, 3, 4, 5], result2)


if __name__ == '__main__':
    unittest.main()
