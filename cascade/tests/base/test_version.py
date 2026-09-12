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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base.utils import Version


def test_comparisons():
    assert Version("0.0") < Version("0.1")
    assert Version("0.0") < Version("1.0")
    assert Version("0.0") < Version("1.1")

    assert Version("1.1") > Version("0.0")
    assert Version("1.1") > Version("0.1")
    assert Version("1.1") > Version("1.0")

    assert Version("0.0") == Version("0.0")
    assert Version("2.5") != Version("3.3")

    assert Version("0.0") <= Version("0.0")
    assert Version("0.0") <= Version("1.0")

    assert Version("1.0") >= Version("1.0")
    assert Version("1.0") >= Version("0.0")


def test_comparison_with_str():
    assert Version("0.0") < "0.1"
    assert "0.1" > Version("0.0")

    assert "0.1" == Version("0.1")
    assert Version("0.0") == "0.0"

    assert Version("2.5") != "3.3"


def test_hashable():
    assert {Version("0.0"), Version("0.1")}
