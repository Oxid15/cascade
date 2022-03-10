from unittest import TestCase
from models import ModelRepo
from dummy_model import DummyModel
import os
import shutil


class TestModelRepo(TestCase):
    def test_repo(self):
        repo = ModelRepo('./models', DummyModel)
        repo.new_line('dummy_1')
        repo.new_line()

        model_line = repo[0]
        model_line = repo[1]

        self.assertTrue(os.path.exists('./models/dummy_1'))
        self.assertTrue(os.path.exists('./models/00001'))

        shutil.rmtree('./models')
        self.assertEqual(2, len(repo))
