import os
import sys
import unittest
from unittest import TestCase

# sys.path.append(os.path.abspath('../..'))
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
