from datetime import datetime
from typing import List, Dict


class Model:
    """
    Base class for any model.
    Used to provide unified interface to any model, store metadata including metrics.
    """
    def __init__(self,  **kwargs) -> None:
        """
        Should be called in any successor - initializes default meta needed.
        Arguments passed in it should be related to model's hyperparameters, architecture.
        All additional arguments should have defaults.
        """
        self.metrics = {}
        self.created_at = datetime.now()

    def fit(self, *args, **kwargs):
        """
        Method to encapsulate training loops.
        May be provided with any training-related arguments.
        """
        raise NotImplementedError()

    def predict(self, *args, **kwargs):
        """
        Method to encapsulate inference.
        May include preprocessing steps to make model self-sufficient.
        """
        raise NotImplementedError()

    def evaluate(self, *args, **kwargs) -> None:
        """
        Evaluates model against any metrics. Should not return any values, just populating self.metrics dict.
        """
        raise NotImplementedError()

    def load(self, filepath) -> None:
        """
        Loads model from provided filepath. May be unpickling process or reading json configs.
        Does not return any model, just restores internal state.
        """
        raise NotImplementedError()

    def save(self, filepath) -> None:
        """
        Saves model's state using provided filepath.
        """
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        meta = [{
            'created_at': self.created_at,
            'metrics': self.metrics
        }]
        return meta
