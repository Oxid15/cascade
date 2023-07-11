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

import json
from typing import Any, List

from ...models import BasicModel


class ConstantBaseline(BasicModel):
    """
    Constant function. This baseline can be used for
    any classification task. It returns only one class
    (for example it can be majority class)
    """

    def __init__(self, constant: Any = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._constant = constant

    def fit(self, x: Any, y: Any, *args: Any, **kwargs: Any) -> None:
        pass

    def predict(self, x: Any, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Returns the array of the same shape as input full of
        given constant.
        """
        return [self._constant for _ in range(len(x))]

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({"constant": self._constant}, f)

    @classmethod
    def load(cls, path: str) -> "ConstantBaseline":
        with open(path, "r") as f:
            obj = json.load(f)
            model = ConstantBaseline(obj["constant"])
            return model
