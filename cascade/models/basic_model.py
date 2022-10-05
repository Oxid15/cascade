"""
Copyright 2022 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from typing import Dict, Callable
from .model import Model, ModelModifier


class BasicModel(Model):
    """
    Basic model is a more concrete version of an abstract Model class.
    It provides common interface for all ML solutions. For more flexible interface
    refer to Model class.

    See also
    --------
    cascade.models.Model
    """

    def load(self, filepath) -> None:
        raise NotImplementedError()

    def save(self, filepath) -> None:
        raise NotImplementedError()

    def predict(self, x, *args, **kwargs):
        raise NotImplementedError()

    def evaluate(self, x, y, metrics_dict: Dict[str, Callable], *args, **kwargs) -> None:
        """
        Receives x and y validation sequences. Passes x to the model's predict
        method along with any args or kwargs needed.
        Then updates self.metrics with what functions in `metrics_dict` return.
        `metrics_dict` should contain names of the metrics and the functions with the interface:
        f(true, predicted) -> metric_value, where metric_value is not always scalar, can be
        array or dict. For example confusion matrix.

        Parameters
        ----------
            x:
                Input of the model.
            y:
                Desired output to compare with the values predicted.
            metrics_dict: Dict[str, Callable]
                Dictionary with functions that given ground-truth and
                predicted values return metrics.
        """
        preds = self.predict(x, *args, **kwargs)
        self.metrics.update({key: metrics_dict[key](y, preds) for key in metrics_dict})

    def fit(self, x, y, *args, **kwargs) -> None:
        raise NotImplementedError()


class BasicModelModifier(ModelModifier, BasicModel):
    """
    Interface to unify BasicModel and ModelModifier.
    """
