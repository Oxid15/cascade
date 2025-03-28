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

from cascade.data import IteratorModifier, IteratorWrapper, Modifier, Wrapper


def test_iter_of_modifier():
    d = Wrapper([1, 2, 3, 4, 5])
    m = Modifier(d)

    result1 = []
    for item in d:
        result1.append(item)

    result2 = []
    for item in m:
        result2.append(item)

    assert [1, 2, 3, 4, 5] == result1
    assert [1, 2, 3, 4, 5] == result2


def test_iter_of_IteratorModifier():
    d = IteratorWrapper([1, 2, 3, 4, 5])
    m = IteratorModifier(d)

    result1 = []
    for item in d:
        result1.append(item)

    result2 = []
    for item in m:
        result2.append(item)

    assert [1, 2, 3, 4, 5] == result1
    assert [1, 2, 3, 4, 5] == result2
