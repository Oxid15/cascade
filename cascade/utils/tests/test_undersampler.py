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

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Wrapper
from cascade.utils.samplers import UnderSampler


@pytest.mark.parametrize(
    "arr, res",
    [
        ([("a", 0), ("b", 0), ("c", 0)], [("a", 0), ("b", 0), ("c", 0)]),
        (
            [("a", 2), ("b", 2), ("c", 2), ("d", 1), ("e", 1)],
            [("d", 1), ("e", 1), ("a", 2), ("b", 2)],
        ),
        ([("a", 0), ("b", 0), ("c", 1)], [("a", 0), ("c", 1)]),
        ([("a", 0), ("b", 0), ("c", 1), ("d", 2)], [("a", 0), ("c", 1), ("d", 2)]),
        ([("a", 2), ("b", 2), ("c", 2), ("d", 1)], [("d", 1), ("a", 2)]),
    ],
)
def test(arr, res):
    ds = Wrapper(arr)
    ds = UnderSampler(ds)

    assert res == [ds[i] for i in range(len(ds))]
