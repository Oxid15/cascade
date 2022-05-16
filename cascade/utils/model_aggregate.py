from ..models import Model


class ModelAggregate(Model):
    def __init__(self, model_cls, **kwargs):
        super().__init__(**kwargs)
        self.models = []

    def fit(self, *args, **kwargs):
        pass

    def predict(self, *args, **kwargs):
        pass

    def evaluate(self, *args, **kwargs) -> None:
        pass

    def load(self, filepath) -> None:
        pass

    def save(self, filepath) -> None:
        pass
