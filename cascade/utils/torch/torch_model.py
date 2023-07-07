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

import pickle
import os
from typing import Any, Type, Union

import torch

from ...base import PipeMeta
from ...models import Model


class TorchModel(Model):
    """
    The wrapper around `nn.Module`s.
    """

    def __init__(
        self,
        model_class: Union[Type, None] = None,
        model: Union[torch.nn.Module, None] = None,
        **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        model_class: type, optional
            The class created when new nn.Module was defined. Will be used
            to construct model. If any arguments needed, please pass them
            into `kwargs`.
        model: torch.nn.Module, optional
            The module that should be used as a model. Have higher priority
            if provided. model_class and model cannot both be None.
        """
        if model is not None:
            self._model = model
        elif model_class is not None:
            self._model = model_class(**kwargs)
        else:
            raise ValueError("Either `model_class` or `model` should be not None")
        super().__init__(**kwargs)

    def predict(self, *args, **kwargs) -> Any:
        """
        Calls internal module with arguments provided.
        """
        return self._model(*args, **kwargs)

    def save(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves the model using `torch.save`.
        If path is the folder, then creates it and
        saves as 'model'
        Args and kwargs are passed into torch.save

        The model is saved in two parts - the wrapper
        and the actual torch model as checkpoint separately.
        This is done for artifact portability - you can use checkpoint in
        deployments directly without the need to bring additional dependency
        with the wrapper. At the same time additional params can still be loaded
        using wrapper that is saved nearby.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            model_path = os.path.join(path, "model.pkl")
            checkpoint_path = os.path.join(path, "checkpoint.pt")
        else:
            model_path = path
            checkpoint_path = os.path.join(*os.path.split(path)[:-1], "checkpoint.pt")

        with open(checkpoint_path, "wb") as f:
            torch.save(self._model, f, *args, **kwargs)
        model = self._model
        del self._model
        with open(model_path, "wb") as f:
            pickle.dump(self, f)
        self._model = model

    @classmethod
    def load(cls, path: str, *args: Any, **kwargs: Any) -> "TorchModel":
        """
        Loads the model using `torch.load`.
        If path is folder, then tries to load 'checkpoint.pt'
        from it.
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            model_path = os.path.join(path, "model.pkl")
            checkpoint_path = os.path.join(path, "checkpoint.pt")
        else:
            model_path = path
            checkpoint_path = os.path.join(*os.path.split(path)[:-1], "checkpoint.pt")

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        with open(checkpoint_path, "rb") as f:
            torch_model = torch.load(f, *args, **kwargs)

        model._model = torch_model
        return model

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["module"] = repr(self._model)
        return meta
