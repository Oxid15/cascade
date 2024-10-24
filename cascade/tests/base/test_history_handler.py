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

import datetime
import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))
from cascade.base import HistoryHandler, MetaHandler
from cascade.data import Wrapper, Modifier


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_repo(tmp_path_str, ext):
    tmp_path = os.path.join(tmp_path_str, "history" + ext)
    hl = HistoryHandler(tmp_path)

    obj = {"a": 0, "b": datetime.datetime.now()}

    hl.log(obj)
    obj_from_file = MetaHandler.read(tmp_path)

    assert "history" in obj_from_file
    assert "type" in obj_from_file
    assert len(obj_from_file["history"]) == 0
    assert obj_from_file["type"] == "history"

    obj = {"a": 1, "b": datetime.datetime.now()}

    hl.log(obj)
    obj_from_file = MetaHandler.read(tmp_path)

    assert "history" in obj_from_file
    assert "type" in obj_from_file
    assert len(obj_from_file["history"]) == 1
    assert obj_from_file["history"][0]["id"] == 0


def test_get_state(tmp_path_str):
    hl = HistoryHandler(os.path.join(tmp_path_str, "diff_history.yml"))

    ds = Wrapper([1, 2])
    meta1 = ds.get_meta()
    hl.log(meta1)

    ds = Modifier(ds)
    meta2 = ds.get_meta()
    hl.log(meta2)

    assert hl.get(0) == meta1
    assert hl.get(1) == meta2
    assert len(hl) == 2


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_serialization_type_casts(tmp_path_str, ext):
    """
    Test that diff is zero although type changed while
    serializing e.g. some field in meta was tuple, but
    became list
    """

    hl = HistoryHandler(os.path.join(tmp_path_str, "diff_history" + ext))

    ds = Wrapper([0, 1, 2])
    ds.update_meta({"special_field": ("tuple", "that with become list")})

    hl.log(ds.get_meta())
    hl.log(ds.get_meta())
    hl.log(ds.get_meta())

    assert len(hl) == 1

    hl = HistoryHandler(os.path.join(tmp_path_str, "diff_history" + ext))
    hl.log(ds.get_meta())

    assert len(hl) == 1
