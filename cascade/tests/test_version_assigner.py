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

from cascade.data import Wrapper, ApplyModifier, VersionAssigner, Concatenator


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test(tmp_path, ext):
    filepath = os.path.join(tmp_path, 'ds' + ext)

    ds = Wrapper([0, 1, 2, 3, 4])
    ds = VersionAssigner(ds, filepath)

    assert ds.version == '0.0'
    assert ds.get_meta()[0]['version'] == '0.0'

    ds = Wrapper([0, 1, 2, 3, 4])
    ds = ApplyModifier(ds, lambda x: x ** 2)
    ds = VersionAssigner(ds, filepath)

    assert ds.version == '1.0'

    ds = Wrapper([0, 1, 2, 3, 4, 5])
    ds = ApplyModifier(ds, lambda x: x ** 2)
    ds = VersionAssigner(ds, filepath)

    assert ds.version == '1.1'


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_deep_changes(tmp_path, ext):
    filepath = os.path.join(tmp_path, 'ds' + ext)

    ds = Wrapper([0, 1, 2, 3, 4])
    ds = ApplyModifier(ds, lambda x: x * 2)
    ds = Concatenator([ds, ds])
    ds = Concatenator([ds, ds])
    ds = VersionAssigner(ds, filepath)

    assert ds.version == '0.0'

    ds = Wrapper([0, 1, 2, 3, 4])
    ds = ApplyModifier(ds, lambda x: x * 2)
    ds = ApplyModifier(ds, lambda x: x * 2)
    ds = Concatenator([ds, ds])
    ds = Concatenator([ds, ds])
    ds = VersionAssigner(ds, filepath)

    assert ds.version == '1.0'
