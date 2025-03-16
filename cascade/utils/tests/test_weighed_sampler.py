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

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

import cascade.data as cdd
from cascade.utils.samplers import WeighedSampler


def test():
    ds = cdd.Wrapper([(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)])

    # Over and under sampling simultaneously
    ds = WeighedSampler(ds, {0: 3, 1: 4})

    assert [item for item in ds] == [
        (0, 0),
        (1, 0),
        (0, 0),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
    ]

    ds = cdd.Wrapper([(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)])

    # Remove label using zero and sample exact number
    ds = WeighedSampler(ds, {0: 0, 1: 5})

    assert [item for item in ds] == [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]

    ds = cdd.Wrapper([(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)])

    # Omit mapping
    ds = WeighedSampler(ds)

    assert [item for item in ds] == [
        (0, 0),
        (1, 0),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
    ]


def test_str_labels():
    ds = cdd.Wrapper(
        [
            (0, "bar"),
            (1, "bar"),
            (2, "foo"),
            (3, "foo"),
            (4, "foo"),
            (5, "foo"),
            (6, "foo"),
        ]
    )

    ds = WeighedSampler(ds, {"bar": 3, "foo": 2})

    assert [item for item in ds] == [
        (0, "bar"),
        (1, "bar"),
        (0, "bar"),
        (2, "foo"),
        (3, "foo"),
    ]


def test_missing_class():
    ds = cdd.Wrapper(
        [
            (0, "bar"),
            (1, "bar"),
            (2, "foo"),
            (3, "foo"),
            (4, "foo"),
            (5, "foo"),
            (6, "foo"),
        ]
    )

    # Raise if class is missing in dataset
    with pytest.raises(ValueError):
        ds = WeighedSampler(ds, {"bar": 3, "foo": 2, "spam": 20})
