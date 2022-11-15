"""
Copyright 2022 Ilia Moiseev

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

import cascade.data as cdd
from cascade.utils import WeighedSampler


def test():
    ds = cdd.Wrapper(
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 1)
        ]
    )

    ds = WeighedSampler(ds, {0: 3, 1: 4})

    assert [item for item in ds] == [
        (0, 0),
        (1, 0),
        (0, 0),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1)
    ]

    ds = cdd.Wrapper(
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 1)
        ]
    )

    ds = WeighedSampler(ds, {0: 0, 1: 5})

    assert [item for item in ds] == [
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1)
    ]

    ds = cdd.Wrapper(
        [
            (0, 0),
            (1, 0),
            (2, 1),
            (3, 1),
            (4, 1),
            (5, 1),
            (6, 1)
        ]
    )

    ds = WeighedSampler(ds)

    assert [item for item in ds] == [
        (0, 0),
        (1, 0),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1)
    ]
