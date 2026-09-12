"""
Copyright 2022-2026 Ilia Moiseev

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
from cascade.utils.samplers import OverSampler


@pytest.mark.parametrize(
    "arr, res",
    [
        ([(1, 0), (2, 0)], [(1, 0), (2, 0)]),
        ([(1, 0), (2, 0), (3, 1)], [(1, 0), (2, 0), (3, 1), (3, 1)]),
        (
            [(1, 0), (2, 0), (3, 1), (4, 2)],
            [(1, 0), (2, 0), (3, 1), (4, 2), (3, 1), (4, 2)],
        ),
        (
            [(1, 2), (2, 2), (3, 2), (4, 1)],
            [(1, 2), (2, 2), (3, 2), (4, 1), (4, 1), (4, 1)],
        ),
        (
            [("1", 2), ("2", 2), ("3", 2), ("4", 1)],
            [("1", 2), ("2", 2), ("3", 2), ("4", 1), ("4", 1), ("4", 1)],
        ),
        (
            [(0, 0), (0, 0), (0, 1), (0, 0)],
            [(0, 0), (0, 0), (0, 1), (0, 0), (0, 1), (0, 1)],
        ),
        (
            [("1", 2), ("2", 2), ("3", 2), ("4", 1), ("5", 1)],
            [("1", 2), ("2", 2), ("3", 2), ("4", 1), ("5", 1), ("4", 1)],
        ),
        (
            [
                ("01", 0),
                ("02", 0),
                ("03", 0),
                ("04", 0),
                ("05", 0),
                ("06", 0),
                ("07", 0),
                ("08", 0),
                ("09", 1),
                ("10", 1),
                ("11", 1),
            ],
            [
                ("01", 0),
                ("02", 0),
                ("03", 0),
                ("04", 0),
                ("05", 0),
                ("06", 0),
                ("07", 0),
                ("08", 0),
                ("09", 1),
                ("10", 1),
                ("11", 1),
                ("09", 1),
                ("10", 1),
                ("11", 1),
                ("09", 1),
                ("10", 1),
            ],
        ),
    ],
)
def test(arr, res):
    ds = Wrapper(arr)
    ds = OverSampler(ds)

    assert res == [ds[i] for i in range(len(ds))]
