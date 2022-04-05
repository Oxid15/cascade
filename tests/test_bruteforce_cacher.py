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


if __name__ == '__main__':
    unittest.main()
