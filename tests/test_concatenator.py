import unittest
from unittest import TestCase
from cascade import Dataset, Concatenator


class TestConcatenator(TestCase):
    def test_concatenation(self):
        class NumberDataset(Dataset):
            def __init__(self, arr):
                self.numbers = arr

            def __getitem__(self, index):
                return self.numbers[index]

            def __len__(self):
                return len(self.numbers)

        n1 = NumberDataset([0, 1])
        n2 = NumberDataset([2, 3, 4, 5])
        n3 = NumberDataset([6, 7, 8])
        n4 = NumberDataset([1])

        c = Concatenator([n1, n2, n4, n3, n4])
        self.assertEqual([c[i] for i in range(len(c))],
                         [0, 1, 2, 3, 4, 5, 1, 6, 7, 8, 1])


if __name__ == '__main__':
    unittest.main()
