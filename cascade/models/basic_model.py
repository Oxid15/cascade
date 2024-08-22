"""
Copyright 2022-2024 Ilia Moiseev

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


import os
import pickle
import warnings
from hashlib import md5
from typing import Any, Callable, List, Union

from ..base import MetaHandler, raise_not_implemented
from ..metrics import Metric, MetricType
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

    def fit(self, x: Any, y: Any, *args: Any, **kwargs: Any) -> None:
        raise_not_implemented("cascade.models.BasicModel", "fit")

    def predict(self, x: Any, *args: Any, **kwargs: Any) -> Any:
        raise_not_implemented("cascade.models.BasicModel", "predict")

    def evaluate(
        self,
        x: Any,
        y: Any,
        metrics: List[Union[Metric, Callable[[Any, Any], MetricType]]],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Receives x and y validation sequences. Passes x to the model's predict
        method along with any args or kwargs needed.
        Then updates self.metrics with what objects in ``metrics`` return.
        ``metrics`` should contain Metric with compute() method or callables with the interface:
        f(true, predicted) -> metric_value, where metric_value is a scalar

        Parameters
        ----------
            x: Any
                Input of the model.
            y: Any
                Desired output to compare with the values predicted.
            metrics: List[Union[Metric, Callable[[Any, Any], MetricType]]]
                List of metrics or callables to compute metric values
        """
        preds = self.predict(x, *args, **kwargs)
        for metric in metrics:
            if isinstance(metric, Metric):
                metric.compute(y, preds)
                self.add_metric(metric)
            elif isinstance(metric, Callable):
                value = metric(y, preds)
                self.add_metric(metric.__name__, value)
            else:
                # Will not raise to not to interrupt evaluation
                warnings.warn(
                    f"Cannot compute metric of type {type(metric)}"
                )

    @classmethod
    def _check_model_hash(cls, path: str) -> None:
        root = os.path.dirname(path)
        meta = MetaHandler.read_dir(root)
        # Uses first meta in list
        # Usually the list is of unit length
        meta = meta[0]
        if "md5sum" in meta:
            with open(path, "rb") as f:
                file_hash = md5(f.read()).hexdigest()
            if file_hash != meta["md5sum"]:
                raise RuntimeError(
                    f".pkl model hash check failed "
                    f"it may be that model's .pkl file was corrupted\n"
                    f'hash from meta: {meta["md5sum"]}\n'
                    f"hash of {path}: {file_hash}"
                )

    @classmethod
    def load(cls, path: str, check_hash: bool = True) -> "BasicModel":
        """
        Loads the model from path provided. Path should be a folder
        """
        if not os.path.isdir(path):
            raise ValueError(f"Error when loading a model - {path} is not a folder")
        path = os.path.join(path, "model.pkl")

        # TODO: enable hash check later
        # if check_hash:
        #     cls._check_model_hash(path)

        with open(path, "rb") as f:
            model = pickle.load(f)
        return model

    def save(self, path: str) -> None:
        """
        Saves model to the path provided
        Also copies any additional files in the model folder.

        Path should be a folder, which will be created
        if not exists and saves there as ``model.pkl``
        """
        super().save(path)

        path = os.path.join(path, "model.pkl")

        with open(path, "wb") as f:
            pickle.dump(self, f)

    def save_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        BasicModel implements this for compatibility.
        This method does nothing since there are no internal artifacts in BasicModel
        """
        pass

    def load_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        BasicModel implements this for compatibility.
        This method does nothing since there are no internal artifacts in BasicModel
        """
        pass


class BasicModelModifier(ModelModifier, BasicModel):
    """
    Interface to unify BasicModel and ModelModifier.
    """
