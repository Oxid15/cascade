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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import dataset, modifier
from cascade.data.functions import FDataset, FModifier

def test_dataset():
    @dataset
    def read_data():
        return [0, 1, 2]
    
    x = read_data()

    assert isinstance(x, FDataset)
    assert x.result == [0, 1, 2]


def test_modifier():
    @dataset
    def read_data():
        return [0, 1, 2]
    
    @modifier
    def square(x):
        return [i**2 for i in x]
    
    x = read_data()
    x = square(x)

    assert isinstance(x, FModifier)
    assert x.result == [0, 1, 4]
    meta = x.get_meta()
    assert len(meta) == 2


def test_multiple_inputs():
    @dataset
    def read_data():
        return [0, 1, 2]

    @modifier
    def sum_two(x, y):
        return [i + j for i, j in zip(x, y)]

    x = read_data()
    x = sum_two(x, x)

    assert isinstance(x, FModifier)
    assert x.result == [0, 2, 4]
    meta = x.get_meta()
    assert len(meta) == 2
    assert len(meta[1]) == 2 # This means two inputs at the first stage
