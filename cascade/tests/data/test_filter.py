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
import random
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from cascade.data import Filter, IteratorDataset, IteratorFilter, Wrapper


@pytest.mark.parametrize(
    "arr, func, res",
    [
        ([1, 2, 3, 4, 5], lambda x: x < 2, [1]),
        (["a", "aa", "aaa", ""], lambda x: len(x), ["a", "aa", "aaa"]),
    ],
)
def test_filter(arr, func, res):
    ds = Wrapper(arr)
    ds = Filter(ds, func)
    assert [item for item in ds] == res


def test_empty_filter():
    ds = Wrapper([0, 1, 2, 3, 4])

    with pytest.raises(AssertionError):
        ds = Filter(ds, lambda x: x > 4)


def test_runtime_error():
    def two_is_bad(i):
        if i == 2:
            raise ValueError("No, 2 is bad!!!")
        return True

    ds = Wrapper([0, 1, 2, 3])

    with pytest.raises(RuntimeError):
        ds = Filter(ds, two_is_bad)


def test_iter():
    class RandomDataStream(IteratorDataset):
        def __next__(self):
            if random.random() < 0.2:
                raise StopIteration()
            else:
                return random.randint(0, 255)

    ds = RandomDataStream()
    ds = IteratorFilter(ds, lambda x: x < 127)

    assert all([item < 127 for item in ds])


def test_empty_iter():
    class EmptyStream(IteratorDataset):
        def __next__(self):
            raise StopIteration()

    ds = EmptyStream()
    ds = IteratorFilter(ds, lambda x: True)

    assert [] == [item for item in ds]
