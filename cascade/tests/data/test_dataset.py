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
import json
import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import BaseDataset, IteratorWrapper, Modifier, Sampler, Wrapper


class DummyDataset(BaseDataset):
    def __len__(self):
        return 0
    
    def __getitem__(self, index) -> None:
        return None


def test_meta():
    now = datetime.datetime.now()
    ds = DummyDataset()
    ds.update_meta({"time": now})
    meta = ds.get_meta()

    assert type(meta) is list
    assert len(meta) == 1
    assert type(meta[0]) is dict
    assert meta[0]["time"] == now
    assert "name" in meta[0]


def test_update_meta():
    ds = DummyDataset()
    ds.update_meta({"a": 1, "b": 2})
    ds.update_meta({"b": 3})
    meta = ds.get_meta()

    assert meta[0]["a"] == 1
    assert meta[0]["b"] == 3


# This is deprecated since 0.13.0
@pytest.mark.skip
def test_meta_from_file(tmp_path):
    with open(os.path.join(tmp_path, "test_meta_from_file.json"), "w") as f:
        json.dump({"a": 1}, f)

    ds = DummyDataset(meta_prefix=os.path.join(tmp_path, "test_meta_from_file.json"))
    meta = ds.get_meta()

    assert "a" in meta[0]
    assert meta[0]["a"] == 1


def test_iterator():
    it = IteratorWrapper([1, 2, 3, 4])
    res = []
    for item in it:
        res.append(item)
    assert [1, 2, 3, 4] == res


def test_wrapper():
    wr = Wrapper([1, 2, 3, 4])
    res = []
    for i in range(len(wr)):
        res.append(wr[i])
    assert [1, 2, 3, 4] == res


def test_modifier():
    ds = Wrapper([1, 2, 3, 4])
    ds = Modifier(ds)

    res = []
    for i in range(len(ds)):
        res.append(ds[i])
    assert [1, 2, 3, 4] == res

    res = []
    for it in ds:
        res.append(it)
    assert [1, 2, 3, 4] == res


def test_modifier_meta():
    ds = Wrapper([1, 2, 3, 4])
    ds = Modifier(ds)

    meta = ds.get_meta()
    assert type(meta) is list
    assert len(meta) == 2


def test_modifier_from_meta():
    ds = Wrapper([1, 2, 3])
    ds.update_meta({"a": 1})
    ds = Modifier(ds)
    ds.update_meta({"b": 0})
    meta = ds.get_meta()

    ds = Wrapper([1, 2, 3])
    ds = Modifier(ds)
    ds.from_meta(meta)

    # The order of objects is from latest to oldest
    assert meta[0]["b"] == 0
    assert meta[1]["a"] == 1


def test_sampler():
    ds = Wrapper([1, 2, 3, 4])
    ds = Sampler(ds, 10)
