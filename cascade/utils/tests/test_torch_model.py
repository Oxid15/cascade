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

import torch

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))


from cascade.utils.torch import TorchModel


def test_save_load(tmp_path_str):
    model = TorchModel(torch.nn.Linear, in_features=10, out_features=2)

    model.save(tmp_path_str)

    assert model._model

    model = TorchModel.load(tmp_path_str)

    assert model.params.get("in_features") == 10
    assert model.params.get("out_features") == 2


def test_model_artifacts(tmp_path_str):
    model = TorchModel(torch.nn.Linear, in_features=10, out_features=2)

    model.save_artifact(tmp_path_str)

    model = TorchModel()
    model.load_artifact(tmp_path_str)

    assert str(model._model) == str(torch.nn.Linear(10, 2))
