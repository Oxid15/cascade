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

import os
from typing import Type, Any
import torch
from ..models import Model
from ..base import PipeMeta


class TorchModel(Model):
    """
    The wrapper around `nn.Module`s.
    """
    def __init__(self, model_class: Type, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        model_class: type
            The class created when new nn.Module was defined. Will be used
            to construct model. If any arguments needed, please pass them
            into `args` and `kwargs`.
        """
        self._model = model_class(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def predict(self, *args, **kwargs) -> Any:
        """
        Calls internal module with whatever arguments.
        """
        return self._model(*args, **kwargs)

    def save(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves the model using `torch.save`.
        If path is the folder, then creates it and
        saves as 'model'
        Args and kwargs are passed into torch.save
        """
        if os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            path = os.path.join(path, "model")

        with open(path, 'wb') as f:
            torch.save(self._model, f, *args, **kwargs)

    def load(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Loads the model using `torch.load`.
        If path is folder, then tries to load 'model'
        from it.
        """
        if os.path.isdir(path):
            path = os.path.join(path, "model")

        with open(path, 'rb') as f:
            self._model = torch.load(f)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]['module'] = repr(self._model)
        return meta
