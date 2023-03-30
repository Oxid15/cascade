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

from cascade.data import Wrapper
from cascade.data import Composer


def test_meta():
    n1 = Wrapper([0, 1, 2, 3])
    n2 = Wrapper([2, 3, 4, 5])

    c = Composer([n1, n2], meta_prefix={'num': 1})
    assert c.get_meta()[0]['num'] == 1
    assert len(c.get_meta()[0]['data']) == 2


@pytest.mark.parametrize(
    'datasets', [
        (Wrapper([0]), Wrapper([0]), Wrapper([0])),
        (Wrapper([1, 2, 3, 4]), Wrapper([2, 3, 4, 5]))
    ]
)
def test_composition(datasets):
    c = Composer(datasets)

    assert [item for item in zip(*datasets)] == [item for item in c]


@pytest.mark.parametrize(
    'datasets', [
        (Wrapper([0]), Wrapper([0, 1, 2]), Wrapper([0])),
        (Wrapper([1, 2, 3, 4]), Wrapper([4, 5])),
        (Wrapper([1, 2, 3, 4]), Wrapper([1, 2, 3, 4]), Wrapper([1, 2, 3]))
    ]
)
def test_different_lengths(datasets):
    with pytest.raises(ValueError):
        Composer(datasets)
