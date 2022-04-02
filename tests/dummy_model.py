import os
import sys
import numpy as np

sys.path.append(os.path.abspath('..'))
from models import Model


class DummyModel(Model):
    def __init__(self):
        super().__init__()
        self.model = b'model'

    def fit(self, *args, **kwargs):
        pass

    def predict(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs):
        self.metrics.update({'acc': np.random.random()})

    def load(self, path_wo_ext):
        with open(f'{path_wo_ext}.bin', 'rb') as f:
            self.model = str(f.read())

    def save(self, path_wo_ext):
        with open(f'{path_wo_ext}.bin', 'wb') as f:
            f.write(b'model')
