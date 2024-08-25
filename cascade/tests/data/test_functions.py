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
import sys

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import dataset, modifier
from cascade.data.functions import FunctionDataset, FunctionModifier


def test_dataset():
    def read_data():
        return [0, 1, 2]

    x = dataset(read_data)()

    assert isinstance(x, FunctionDataset)
    assert x.result == [0, 1, 2]


def test_modifier():
    def read_data():
        return [0, 1, 2]

    def square(x):
        return [i**2 for i in x]

    x = dataset(read_data)()
    x = modifier(square)(x)

    assert isinstance(x, FunctionModifier)
    assert x.result == [0, 1, 4]
    meta = x.get_meta()
    assert len(meta) == 2


def test_multiple_inputs():
    def read_data():
        return [0, 1, 2]

    def sum_two(x, y):
        return [i + j for i, j in zip(x, y)]

    x = dataset(read_data)()
    x = modifier(sum_two)(x, x)

    assert isinstance(x, FunctionModifier)
    assert x.result == [0, 2, 4]
    meta = x.get_meta()
    assert len(meta) == 2
    assert len(meta[1]) == 2  # This means two inputs at the first stage
