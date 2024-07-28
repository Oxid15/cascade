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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import ApplyModifier, Wrapper
from cascade.lines import DataLine


def add1(x):
    return x + 1


def test_save_load(tmp_path_str):
    ds = Wrapper([0, 1, 2])
    ds = ApplyModifier(ds, add1)

    line = DataLine(tmp_path_str)
    line.save(ds)

    ds = ApplyModifier(ds, add1)
    line.save(ds)

    ds01 = line.load("0.1")
    ds10 = line.load("1.0")

    assert [1, 2, 3] == [i for i in ds01]
    assert [2, 3, 4] == [i for i in ds10]


def test_get_version(tmp_path_str):
    line = DataLine(tmp_path_str)

    ds = Wrapper([0, 1, 2])
    ds01 = ApplyModifier(ds, add1)
    line.save(ds01)

    ds10 = ApplyModifier(ds01, add1)
    line.save(ds10)

    assert str(line.get_version(ds01)) == "0.1"
    assert str(line.get_version(ds10)) == "1.0"


def test_idempotency(tmp_path_str, dataset):
    line = DataLine(tmp_path_str)

    line.save(dataset)
    version = line.get_version(dataset)

    line.save(dataset)
    after_version = line.get_version(dataset)

    assert version == after_version
    assert len(line) == 1


def test_load_obj_meta(tmp_path_str, dataset):
    line = DataLine(tmp_path_str)

    dataset.update_meta({"test_param": 1})
    line.save(dataset)
    version = line.get_version(dataset)

    meta = line.load_obj_meta(str(version))
    assert meta[0]["test_param"] == 1
