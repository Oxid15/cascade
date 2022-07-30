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

import torch
from typing import ClassVar
from ..models import Model


class TorchModel(Model):
    def __init__(self, model_class: ClassVar, *args, **kwargs) -> None:
        self._model = model_class(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def predict(self, *args, **kwargs):
        return self._model(*args, **kwargs)

    def save(self, path, *args, **kwargs) -> None:
        with open(path, 'wb') as f:
            torch.save(self._model, f)

    def load(self, path, *args, **kwargs) -> None:
        with open(path, 'rb') as f:
            self._model = torch.load(f)

    def get_meta(self):
        meta = super().get_meta()
        meta[-1]['module'] = repr(self._model)
        return meta
