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

from typing import Dict, List
import torch
from ..models import Model


class TorchModel(Model):
    """
    The wrapper around `nn.Module`s.
    """
    def __init__(self, model_class: type, *args, **kwargs) -> None:
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

    def predict(self, *args, **kwargs):
        """
        Calls internal module with whatever arguments.
        """
        return self._model(*args, **kwargs)

    def save(self, path: str, *args, **kwargs) -> None:
        """
        Saves the model using `torch.save`.
        """
        with open(path, 'wb') as f:
            # TODO: pass args and kwargs
            torch.save(self._model, f)

    def load(self, path: str, *args, **kwargs) -> None:
        """
        Loads the model using `torch.load`.
        """
        with open(path, 'rb') as f:
            self._model = torch.load(f)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0]['module'] = repr(self._model)
        return meta
