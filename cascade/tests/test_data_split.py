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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

import cascade.data as cdd


def test():
    ds = cdd.Wrapper([0, 1, 2, 3, 4])

    ds1, ds2 = cdd.split(ds)

    assert [item for item in ds1] == [0, 1]
    assert [item for item in ds2] == [2, 3, 4]

    ds1, ds2 = cdd.split(ds, 0.6)

    assert [item for item in ds1] == [0, 1, 2]
    assert [item for item in ds2] == [3, 4]

    ds1, ds2 = cdd.split(ds, num=4)

    assert [item for item in ds1] == [0, 1, 2, 3]
    assert [item for item in ds2] == [4]

    # This means pipeline was made
    assert len(ds1.get_meta()) == 2


def test_wrong_usage():
    ds = cdd.Wrapper([0, 1, 2, 3])

    with pytest.raises(ValueError):
        a, b = cdd.split(ds, None)


def test_empty():
    ds = cdd.Wrapper([])

    with pytest.raises(ValueError):
        a, b = cdd.split(ds, num=10)

    with pytest.raises(ValueError):
        a, b = cdd.split(ds)
