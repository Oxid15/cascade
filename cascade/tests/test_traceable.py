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

from cascade.base import MetaHandler, Traceable, TraceableOnDisk, default_meta_format


def test_meta():
    now = datetime.datetime.now()
    tr = Traceable(meta_prefix={"time": now})
    meta = tr.get_meta()

    assert type(meta) == list
    assert len(meta) == 1
    assert type(meta[0]) == dict
    assert meta[0]["time"] == now
    assert "name" in meta[0]
    assert "description" in meta[0]
    assert "tags" in meta[0]


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


def test_default_meta_fmt(tmp_path):
    tmp_path = str(tmp_path)
    trd = TraceableOnDisk(tmp_path, meta_fmt=None)
    trd._create_meta()

    assert os.path.join(tmp_path, "meta" + default_meta_format)


def test_infer_meta_fmt(tmp_path):
    tmp_path = str(tmp_path)
    trd = TraceableOnDisk(tmp_path, meta_fmt=".yml")
    trd._create_meta()

    trd = TraceableOnDisk(tmp_path, None)

    assert os.path.join(tmp_path, "meta.yml")


def test_infer_meta_fmt_conflict(tmp_path):
    tmp_path = str(tmp_path)
    trd = TraceableOnDisk(tmp_path, meta_fmt=".yml")
    trd._create_meta()

    with pytest.warns(UserWarning):
        trd = TraceableOnDisk(tmp_path, meta_fmt=".json")

    trd._update_meta()
    assert os.path.join(tmp_path, "meta.yml")


def test_descriptions():
    tr = Traceable(description="test")
    assert tr.description == "test"
    tr.describe("test2")
    assert tr.description == "test2"


def test_tags():
    tr = Traceable(tags=["a", "b"])
    tr.tag("c")
    assert tr.tags == {"a", "b", "c"}

    tr.tag(["c", "d"])
    assert tr.tags == {"a", "b", "c", "d"}

    tr.remove_tag("d")
    assert tr.tags == {"a", "b", "c"}

    tr.remove_tag(["a", "b", "c"])
    assert tr.tags == set()


def test_comments():
    tr = Traceable()

    tr.comment("hello")

    assert len(tr.comments) == 1
    assert tr.comments[0].id == "1"
    assert tr.comments[0].message == "hello"
    assert hasattr(tr.comments[0], "user")
    assert hasattr(tr.comments[0], "host")
    assert hasattr(tr.comments[0], "timestamp")


def test_links():
    tr = Traceable()
    tr2 = Traceable(lol=2)

    tr.link(tr2)

    assert len(tr.links) == 1
    assert tr.links[0].meta == tr2.get_meta()
    assert tr.links[0].uri is None

    tr.link(name="link2")

    assert len(tr.links) == 2
    assert tr.links[1].name == "link2"
    assert tr.links[1].uri is None

    tr.link(tr2, include=False)

    assert tr.links[2].meta is not None


def test_from_meta():
    tr = Traceable()
    tr.tag("tag")
    tr.describe("description")
    tr.comment("lol")
    tr.comment("kek")

    meta = tr.get_meta()

    tr = Traceable()
    tr.from_meta(meta[0])

    assert tr.tags == set(["tag"])
    assert tr.description == "description"
    assert [c.message for c in tr.comments] == ["lol", "kek"]
