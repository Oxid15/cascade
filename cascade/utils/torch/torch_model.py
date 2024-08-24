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
from typing import Any, Optional, Type

import torch

from ...base import Meta
from ...models import BasicModel


class TorchModel(BasicModel):
    """
    The wrapper around ``nn.Module``
    """

    def __init__(
        self,
        model_class: Optional[Type] = None,
        model: Optional[torch.nn.Module] = None,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        model_class: type, optional
            The class created when new nn.Module was defined. Will be used
            to construct model. If any arguments needed, please pass them
            into ``kwargs``.
        model: torch.nn.Module, optional
            The module that should be used as a model. Have higher priority
            if provided. model_class and model cannot both be None.
        """
        if model is not None:
            self._model = model
        elif model_class is not None:
            self._model = model_class(**kwargs)

        super().__init__(**kwargs)

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        """
        Calls internal module with arguments provided.
        """
        return self._model(*args, **kwargs)

    def evaluate(self, x: Any, y: Any, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()

    def save(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves model to the path provided.
        Path should be a folder. Creates
        it if not exists and saves there as
        model.pkl

        When saving using this method only wrapper is saved
        if you want to save torch module use save_artifact

        See also
        --------
        cascade.utils.torch.TorchModel.save_artifact
        """
        super().save(path)
        model_path = os.path.join(path, "model.pkl")

        # Save without torch artifact
        model = self._model
        del self._model
        with open(model_path, "wb") as f:
            pickle.dump(self, f)
        self._model = model

    def save_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves torch module. Additional args and kwargs are passed to torch.save

        Parameters
        ----------
        path : str
            the folder in which to save checkpoint.pt

        Raises
        ------
        ValueError
            if the path is not a valid directory
        """
        if not os.path.isdir(path):
            raise ValueError(f"Error when saving an artifact - {path} is not a folder")

        checkpoint_path = os.path.join(path, "checkpoint.pt")
        with open(checkpoint_path, "wb") as f:
            torch.save(self._model, f, *args, **kwargs)

    def load_artifact(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Loads torch module. Additional args and kwargs are passed to torch.load

        Parameters
        ----------
        path : str
            the folder from which to load pipeline.pkl

        Raises
        ------
        ValueError
            if the path is not a valid directory
        """
        if not os.path.isdir(path):
            raise ValueError(f"Error when loading an artifact - {path} is not a folder")

        checkpoint_path = os.path.join(path, "checkpoint.pt")
        with open(checkpoint_path, "rb") as f:
            self._model = torch.load(f, *args, **kwargs)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["module"] = repr(self._model)
        return meta
