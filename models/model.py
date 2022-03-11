from datetime import datetime


class Model:
    def __init__(self):
        self.metrics = {}
        self.created_at = datetime.now()

    def fit(self, *args, **kwargs):
        raise NotImplementedError()

    def predict(self, *args, **kwargs):
        raise NotImplementedError()
    
    def evaluate(self, *args, **kwargs):
        raise NotImplementedError()

    def load(self, filepath):
        raise NotImplementedError()

    def save(self, filepath):
        raise NotImplementedError()

    def get_meta(self) -> dict:
        meta = {
            'created_at': self.created_at,
            'metrics': self.metrics
        }
        return meta
