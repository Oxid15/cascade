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

import datetime
import json
import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler, Traceable, TraceableOnDisk


def test_meta():
    now = datetime.datetime.now()
    tr = Traceable(meta_prefix={"time": now})
    meta = tr.get_meta()

    assert type(meta) == list
    assert len(meta) == 1
    assert type(meta[0]) == dict
    assert meta[0]["time"] == now
    assert "name" in meta[0]


def test_update_meta():
    tr = Traceable(meta_prefix={"a": 1, "b": 2})
    tr.update_meta({"b": 3})
    meta = tr.get_meta()

    assert meta[0]["a"] == 1
    assert meta[0]["b"] == 3


def test_meta_from_file(tmp_path):
    with open(os.path.join(tmp_path, "test_meta_from_file.json"), "w") as f:
        json.dump({"a": 1}, f)

    tr = Traceable(meta_prefix=os.path.join(tmp_path, "test_meta_from_file.json"))
    meta = tr.get_meta()

    assert "a" in meta[0]
    assert meta[0]["a"] == 1


def test_update_meta_from_file(tmp_path):
    with open(os.path.join(tmp_path, "test_meta_from_file.json"), "w") as f:
        json.dump({"a": 1}, f)

    tr = Traceable()
    tr.update_meta(os.path.join(tmp_path, "test_meta_from_file.json"))
    meta = tr.get_meta()

    assert "a" in meta[0]
    assert meta[0]["a"] == 1


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_create(tmp_path, ext):
    tmp_path = str(tmp_path)
    trd = TraceableOnDisk(tmp_path, ext)
    trd._create_meta()

    meta_path = os.path.join(tmp_path, "meta" + ext)

    assert os.path.exists(meta_path)
    assert trd.get_root() == os.path.dirname(meta_path)


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_recreate(tmp_path, ext):
    tmp_path = str(tmp_path)
    trd = TraceableOnDisk(tmp_path, ext)
    trd._create_meta()

    meta_path = os.path.join(tmp_path, "meta" + ext)
    meta = MetaHandler.read(meta_path)

    trd._create_meta()

    new_meta = MetaHandler.read(meta_path)

    assert list(meta[0].keys()) == list(new_meta[0].keys())
    assert meta[0]["created_at"] == new_meta[0]["created_at"]
    assert meta[0]["updated_at"] != new_meta[0]["updated_at"]
