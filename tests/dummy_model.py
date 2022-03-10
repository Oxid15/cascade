from models import Model


class DummyModel(Model):
    def fit(self, *args, **kwargs):
        pass

    def predict(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs):
        pass

    def load(self, path_wo_ext):
        with open(f'{path_wo_ext}.bin', 'rb') as f:
            return str(f.readlines())

    def save(self, path_wo_ext):
        with open(f'{path_wo_ext}.bin', 'wb') as f:
            f.write(b'model')
