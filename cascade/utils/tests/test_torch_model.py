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
import sys

import pytest
import torch

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))


from cascade.utils.torch_model import TorchModel


@pytest.mark.parametrize("postfix", ["", "model", "model.pt"])
def test_save_load(tmp_path, postfix):
    tmp_path = str(tmp_path)

    if postfix:
        tmp_path = os.path.join(tmp_path, postfix)

    model = TorchModel(torch.nn.Linear, in_features=10, out_features=2)

    model.save(tmp_path)

    model = TorchModel.load(tmp_path)

    assert str(model._model) == str(torch.nn.Linear(10, 2))
