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

import pytest

from cascade.data import ApplyModifier, IteratorWrapper, Wrapper

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))


data = [
    ([1, 2, 3, 4, 5], lambda x: x * 2),
    ([1], lambda x: x**2),
    ([1, 2, -3], lambda x: x),
]


@pytest.mark.parametrize("arr, func", data)
def test_apply_modifier(arr, func):
    ds = Wrapper(arr)
    ds = ApplyModifier(ds, func)
    assert list(map(func, arr)) == [item for item in ds]


def test_ds_coverage(dataset):
    ds = ApplyModifier(dataset, lambda x: x)
    for item in ds:
        pass

    if hasattr(dataset, "__len__"):
        for i in range(len(ds)):
            ds[i]


@pytest.mark.parametrize("arr, func", data)
def test_apply_modifier_iterators(arr, func):
    ds = IteratorWrapper(arr)
    ds = ApplyModifier(ds, func)
    assert list(map(func, arr)) == [item for item in ds]


def test_p():
    ds = Wrapper([0, 1, 2, 3])
    ds = ApplyModifier(ds, lambda x: x + 1, 0.5, seed=42)

    assert [i for i in ds] == [0, 2, 3, 4]

    ds = Wrapper([0, 1, 2, 3])
    ds = ApplyModifier(ds, lambda x: x + 1, 1)

    assert [i for i in ds] == [1, 2, 3, 4]

    ds = Wrapper([0, 1, 2, 3])
    ds = ApplyModifier(ds, lambda x: x + 1, 0)

    assert [i for i in ds] == [0, 1, 2, 3]


def test_p_get():
    ds = Wrapper([0, 1, 2, 3])
    ds = ApplyModifier(ds, lambda x: x + 1, 0.5, seed=42)

    assert [ds[i] for i in range(len(ds))] == [0, 2, 3, 4]
