import os
import sys
import unittest
from unittest import TestCase

sys.path.append(os.path.abspath('../..'))
from cascade.models import ModelRepo
from cascade.tests.dummy_model import DummyModel


class TestModelRepo(TestCase):
    def test_repo(self):
        import shutil

        repo = ModelRepo('./models', DummyModel)

        line1 = repo['dummy_1']
        line2 = repo['00001']

        self.assertTrue(os.path.exists('./models/dummy_1'))
        self.assertTrue(os.path.exists('./models/00001'))

        shutil.rmtree('./models')
        self.assertEqual(2, len(repo))


if __name__ == '__main__':
    unittest.main()
