"""
Copyright 2022-2024 Ilia Moiseev

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

from cascade.base.utils import parse_version


@pytest.mark.parametrize(
    "ver,result", [
        ("0.13.0", (0, 13, 0)),
        ("0.13.0-alpha", (0, 13, 0)),
        ("0.0.0", (0, 0, 0)),
        ("0.0.100", (0, 0, 100)),
        ("100.99990.100", (100, 99990, 100)),
        ("v100.99990.100", (100, 99990, 100)),
    ]
)
def test(ver, result):
    assert parse_version(ver) == result
