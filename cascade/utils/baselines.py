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
import json
import numpy as np
from ..models import BasicModel


class ConstantBaseline(BasicModel):
    """
    Constant function. This baseline can be used for
    any classification task. It returns only one class
    (for example it can be majority class)
    """
    def __init__(self, constant=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._constant = constant

    def fit(self, x, y, *args, **kwargs) -> None:
        pass

    def predict(self, x, *args, **kwargs) -> np.ndarray:
        """
        Returns the array of the same shape as input full of
        given constant.
        """
        # TODO: make more universal when work with input shape
        return np.full_like(x, self._constant)

    def save(self, path) -> None:
        with open(path, 'w') as f:
            json.dump({'constant': self._constant}, f)

    def load(self, path) -> None:
        with open(path, 'r') as f:
            obj = json.load(f)
            self._constant = obj['constant']
