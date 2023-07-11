"""
Copyright 2022-2023 Ilia Moiseev

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


import glob
from hashlib import md5
import pickle
import os

from typing import Dict, Callable, Any
from ..base import raise_not_implemented, MetaHandler
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
        metrics_dict: Dict[str, Callable],
        *args: Any,
        **kwargs: Any,
    ) -> None:
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

    @classmethod
    def _check_model_hash(cls, path: str) -> None:
        root = os.path.dirname(path)
        names = glob.glob(os.path.join(f"{root}", "meta.*"))
        if len(names) == 1:
            meta = MetaHandler.read(names[0])
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
                        f'hash from {names[0]}: {meta["md5sum"]}\n'
                        f"hash of {path}: {file_hash}"
                    )
        elif len(names) > 1:
            raise RuntimeError(f"Multiple possible meta-files found: {names}")

    @classmethod
    def load(cls, path: str, check_hash: bool = True) -> "BasicModel":
        """
        Loads the model from path provided. Path may be a folder,
        if so, `model` is assumed.
        """
        if os.path.isdir(path):
            path = os.path.join(path, "model")

        # TODO: enable hash check later
        # if check_hash:
        #     cls._check_model_hash(path)

        with open(path, "rb") as f:
            model = pickle.load(f)
        return model

    def save(self, path: str) -> None:
        """
        Saves model to the path provided.
        If path is a folder, then creates
        it if not exists and saves there as
        `model`
        If path is a file, then saves it accordingly.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            path = os.path.join(path, "model")

        with open(path, "wb") as f:
            pickle.dump(self, f)


class BasicModelModifier(ModelModifier, BasicModel):
    """
    Interface to unify BasicModel and ModelModifier.
    """
