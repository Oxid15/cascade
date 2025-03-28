"""
Copyright 2022-2025 Ilia Moiseev

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

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from cascade.data import SimpleDataloader


@pytest.mark.parametrize(
    "arr, bs, result",
    [
        ([1], 1, [[1]]),
        ([1, 2], 1, [[1], [2]]),
        ([1, 2, 3], 2, [[1, 2], [3]]),
        ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
        ([1, 2, 3, 4], 3, [[1, 2, 3], [4]]),
        ([1, 2, 3, 4], 4, [[1, 2, 3, 4]]),
    ],
)
def test_batches(arr, bs, result):
    dl = SimpleDataloader(arr, batch_size=bs)
    assert list(dl) == result


@pytest.mark.parametrize(
    "arr, bs",
    [
        ([1], 0),
    ],
)
def test_illegal(arr, bs):
    with pytest.raises(ValueError):
        dl = SimpleDataloader(arr, batch_size=bs)


@pytest.mark.parametrize(
    "arr, bs",
    [
        ([1], 2),
        ([1, 2], 1000),
    ],
)
def test_larger_than_sequence(arr, bs):
    dl = SimpleDataloader(arr, batch_size=bs)
    assert list(dl) == [arr]
