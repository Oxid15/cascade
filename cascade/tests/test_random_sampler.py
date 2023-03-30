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
from numpy import random

SEED = 0

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import RandomSampler, Wrapper


@pytest.mark.parametrize(
    'arr, result', [
        ([1, 2, 3, 4, 5], [3, 1, 2, 4, 5]),
        ([1, 5], [5, 1]),
        ([1, 2, -3], [-3, 2, 1])
    ]
)
def test(arr, result):
    random.seed(SEED)

    ds = Wrapper(arr)
    ds = RandomSampler(ds)

    for item, res in zip(ds, result):
        assert item == res


@pytest.mark.parametrize(
    'arr, result', [
        ([1, 2, 3, 4, 5], [3, 1, 2]),
        ([1, 5], [1, 5, 5]),
        ([1, 2, -3], [-3, 2, 1])
    ],
)
def test_over_and_under(arr, result):
    random.seed(SEED)

    ds = Wrapper(arr)
    ds = RandomSampler(ds, 3)

    for item, res in zip(ds, result):
        assert item == res
