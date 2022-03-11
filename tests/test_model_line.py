from unittest import TestCase
from dummy_model import DummyModel
from models.model_repo import ModelLine

import shutil


class TestModelLine(TestCase):
    def test_save(self):
        m = DummyModel()
        line = ModelLine('./line', DummyModel)
        line.save(m)

        shutil.rmtree('./line')  # Cleanup

        self.assertEqual(len(line), 1)
