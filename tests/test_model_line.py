import os
import sys
import unittest
from unittest import TestCase

sys.path.append(os.path.abspath('../..'))
from cascade.tests.dummy_model import DummyModel
from cascade.models.model_repo import ModelLine


class TestModelLine(TestCase):
    def test_save(self):
        import shutil

        m = DummyModel()
        line = ModelLine('./line', DummyModel)
        line.save(m)

        shutil.rmtree('./line')  # Cleanup

        self.assertEqual(len(line), 1)


if __name__ == '__main__':
    unittest.main()
