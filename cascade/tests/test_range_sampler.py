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
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import RangeSampler, Wrapper


def test():
    data = [0, 1, 2, 3, 4]
    ds = Wrapper(data)
    ds = RangeSampler(ds, 2)

    sampled = [item for item in ds]

    assert sampled == [data[i] for i in range(2)]

    ds = Wrapper(data)
    ds = RangeSampler(ds, 1, 3)

    sampled = [item for item in ds]

    assert sampled == [data[i] for i in range(1, 3)]

    ds = Wrapper(data)
    ds = RangeSampler(ds, 0, len(ds), 2)

    sampled = [item for item in ds]

    assert sampled == [data[i] for i in range(0, len(data), 2)]

    with pytest.raises(AssertionError):
        ds = Wrapper(data)
        ds = RangeSampler(data, 10, 0)  # start > stop -> num_samples == 0
