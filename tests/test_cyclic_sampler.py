from unittest import TestCase
from data import CyclicSampler
from number_dataset import NumberDataset


class TestCyclicSampler(TestCase):
    def test_cycle(self):
        ds = NumberDataset([0, 1, 2, 3, 4])
        ds = CyclicSampler(ds, 16)

        self.assertEqual([ds[i] for i in range(len(ds))],
                         [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0])
