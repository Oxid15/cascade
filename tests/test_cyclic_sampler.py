import os
import sys
import unittest
from unittest import TestCase

sys.path.append(os.path.abspath('../..'))
from cascade.data import CyclicSampler
from cascade.tests.number_dataset import NumberDataset


class TestCyclicSampler(TestCase):
    def test_cycle(self):
        ds = NumberDataset([0, 1, 2, 3, 4])
        ds = CyclicSampler(ds, 16)

        self.assertEqual([ds[i] for i in range(len(ds))],
                         [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0])

        self.assertEqual([item for item in ds],
                         [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0])


if __name__ == '__main__':
    unittest.main()
