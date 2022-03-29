import pickle
from sklearn.pipeline import Pipeline

from ..models import Model


class SkClassifier(Model):
    def __init__(self, name=None, blocks=[]):
        super().__init__()
        self.name = name
        if len(blocks):
            self.pipeline = self.construct_pipeline(blocks)

    def construct_pipeline(self, blocks):
        return Pipeline([(str(i), block) for i, block in enumerate(blocks)])

    def fit(self, x, y):
        self.pipeline.fit(x, y)

    def predict(self, x):
        return self.pipeline.predict(x)

    def evaluate(self, x, y, metrics_dict):
        preds = self.predict(x)
        self.metrics.update({key: metrics_dict[key](preds, y) for key in metrics_dict})

    def load(self, path_w_ext):
        with open(path_w_ext, 'rb') as f:
            self.pipeline = pickle.load(f)

    def save(self, path_wo_ext):
        with open(f'{path_wo_ext}.pkl', 'wb') as f:
            pickle.dump(self.pipeline, f)

    def get_meta(self):
        meta = super().get_meta()
        meta.update({
            'name': self.name if self.name is not None else None,
            'pipeline': repr(self.pipeline)
        })
        return meta
