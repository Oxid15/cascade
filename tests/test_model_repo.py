from unittest import TestCase
from models import ModelRepo
from dummy_model import DummyModel
import os
import shutil


class TestModelRepo(TestCase):
    def test_repo(self):
        repo = ModelRepo('./models', DummyModel)

        line1 = repo['dummy_1']
        line2 = repo['00001']

        self.assertTrue(os.path.exists('./models/dummy_1'))
        self.assertTrue(os.path.exists('./models/00001'))

        shutil.rmtree('./models')
        self.assertEqual(2, len(repo))
