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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import CyclicSampler, Wrapper


def test_cycle():
    ds = Wrapper([0, 1, 2, 3, 4])
    ds = CyclicSampler(ds, 16)

    assert [ds[i] for i in range(len(ds))] == [
        0,
        1,
        2,
        3,
        4,
        0,
        1,
        2,
        3,
        4,
        0,
        1,
        2,
        3,
        4,
        0,
    ]


def test():
    ds = CyclicSampler(Wrapper([1]), 2)

    for i in range(len(ds)):
        ds[i]

    for i in ds:
        pass
