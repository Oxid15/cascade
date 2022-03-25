import unittest
from unittest import TestCase
from data import Concatenator
from number_dataset import NumberDataset


class TestConcatenator(TestCase):
    def test_concatenation(self):
        n1 = NumberDataset([0, 1])
        n2 = NumberDataset([2, 3, 4, 5])
        n3 = NumberDataset([6, 7, 8])
        n4 = NumberDataset([1])

        c = Concatenator([n1, n2, n4, n3, n4])
        self.assertEqual([c[i] for i in range(len(c))],
                         [0, 1, 2, 3, 4, 5, 1, 6, 7, 8, 1])
