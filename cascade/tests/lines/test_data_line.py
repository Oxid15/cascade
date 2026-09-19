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
import random
import sys
from typing import Any

import pytest

from cascade.data.data_card import DataCard

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import ApplyModifier, Concatenator, Dataset, Wrapper
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

    assert [1, 2, 3] == list(ds01)
    assert [2, 3, 4] == list(ds10)


def test_get_version(tmp_path_str):
    line = DataLine(tmp_path_str)

    ds = Wrapper([0, 1, 2])
    ds01 = ApplyModifier(ds, add1)
    line.save(ds01)

    ds10 = ApplyModifier(ds01, add1)
    line.save(ds10)

    assert str(line.get_version(ds01)) == "0.1"
    assert str(line.get_version(ds10)) == "1.0"

    ds01.update_meta({"a": 1})
    line.save(ds01)

    assert str(line.get_version(ds01)) == "0.2"

    ds20 = ApplyModifier(ds10, add1)
    line.save(ds20)

    assert str(line.get_version(ds20)) == "2.0"


def test_idempotency(tmp_path_str, dataset):
    line = DataLine(tmp_path_str)

    line.save(dataset)
    version = line.get_version(dataset)

    another_ds = Wrapper([0, 1, 2])
    another_ds.update_meta({"random_param": random.randint(0, 100)})
    line.save(another_ds)

    for _ in range(10):
        line.save(dataset)
        after_version = line.get_version(dataset)

        assert version == after_version
        assert len(line) == 2

    _ = line.load(str(version))
    assert len(line) == 2


def test_idempotency_after_recreation(tmp_path_str):
    def run(tmp_path_str):
        ds = Wrapper([0, 1, 2])

        ds_noise = ApplyModifier(ds, add1)
        ds = Concatenator([ds, ds_noise])
        ds.update_meta(
            {
                "desc": "Hello",
                "param": 1,
            }
        )

        dataline = DataLine(tmp_path_str)
        dataline.save(ds)
        version = dataline.get_version(ds)
        assert str(version) == "0.1"

        ds.update_meta({"a": "b"})
        dataline.save(ds)
        version = dataline.get_version(ds)
        assert str(version) == "0.2"

        changed_ds = ApplyModifier(ds, add1)
        dataline.save(changed_ds)
        version = dataline.get_version(changed_ds)
        assert str(version) == "1.0"

        version = dataline.get_version(ds)
        assert str(version) == "0.2"

        loaded_ds = dataline.load("0.2")
        version = dataline.get_version(loaded_ds)
        assert str(version) == "0.2"

    run(tmp_path_str)
    run(tmp_path_str)


def test_load_obj_meta(tmp_path_str, dataset):
    line = DataLine(tmp_path_str)

    dataset.update_meta({"test_param": 1})
    line.save(dataset)
    version = line.get_version(dataset)

    meta = line.load_obj_meta(str(version))
    assert meta[0]["test_param"] == 1


def test_data_order_after_reload(tmp_path_str):
    line = DataLine(tmp_path_str)

    dataset = Wrapper([])

    for i in range(11):
        # Should bump minor
        dataset.update_meta({"test_param": i})
        line.save(dataset)

    # Should bump major
    dataset = ApplyModifier(dataset, add1)

    for i in range(5):
        dataset.update_meta({"test_param": i})
        line.save(dataset)

    version_2 = line.get_version(line.load(2))

    versions = line.get_item_names()
    assert versions == [
        "0.1",
        "0.2",
        "0.3",
        "0.4",
        "0.5",
        "0.6",
        "0.7",
        "0.8",
        "0.9",
        "0.10",
        "0.11",
        "1.0",
        "1.1",
        "1.2",
        "1.3",
        "1.4",
    ]

    line = DataLine(tmp_path_str)
    versions_after_reload = line.get_item_names()

    assert versions == versions_after_reload

    version_2_after_reload = line.get_version(line.load(2))

    assert version_2 == version_2_after_reload


def test_broken_folder(tmp_path_str):
    dl = DataLine(tmp_path_str)

    ds = Wrapper([0])
    dl.save(ds)

    ds = Wrapper(ds)
    dl.save(ds)

    version = dl.get_version(ds)

    os.remove(os.path.join(tmp_path_str, str(version), "HASHES"))

    with pytest.raises(RuntimeError):
        dl = DataLine(tmp_path_str)


def test_broken_hashes(tmp_path_str):
    dl = DataLine(tmp_path_str)

    ds = Wrapper([0])
    dl.save(ds)

    ds = Wrapper(ds)
    dl.save(ds)

    version = dl.get_version(ds)

    with open(os.path.join(tmp_path_str, str(version), "HASHES"), "w") as f:
        f.write("broken")

    with pytest.raises(RuntimeError):
        dl = DataLine(tmp_path_str)


def test_volatiles_bump_version(tmp_path_str):
    class VolatileDataset(Dataset):
        def get(self, index):
            return index

        def __len__(self):
            return 10

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["random"] = random.random()
            return meta

    dl = DataLine(tmp_path_str)

    ds = VolatileDataset()
    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.2"

    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.3"

    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.4"


def test_declared_volatiles_do_not_bump_version(tmp_path_str):
    class VolatileDataset(Dataset):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.declare_volatiles("random")

        def get(self, index):
            return index

        def __len__(self):
            return 10

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["random"] = random.random()
            return meta

    dl = DataLine(tmp_path_str)

    ds = VolatileDataset()

    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.1"

    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.1"

    dl.save(ds, only_meta=True)

    assert str(dl.get_version(ds)) == "0.1"


def test_mask_volatiles_masks_only_declared_fields(tmp_path_str):
    class VolatileDataset(Dataset):
        def __init__(self, label: str, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.label = label
            self.declare_volatiles("random", "timestamp")

        def get(self, index):
            return index

        def __len__(self):
            return 3

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["label"] = self.label
            meta[0]["random"] = random.random()
            meta[0]["timestamp"] = random.random()
            return meta

    dl = DataLine(tmp_path_str)
    ds1 = VolatileDataset("first")
    ds2 = VolatileDataset("second")

    dl.save(ds1, only_meta=True)
    first_version = dl.get_version(ds1)

    dl.save(ds2, only_meta=True)
    second_version = dl.get_version(ds2)

    assert str(first_version) == "0.1"
    assert str(second_version) == "0.2"

    ds3 = VolatileDataset("second")
    dl.save(ds3, only_meta=True)
    assert str(dl.get_version(ds3)) == "0.2"


def test_mask_volatiles_keeps_non_volatile_fields_in_versioning(tmp_path_str):
    dl = DataLine(tmp_path_str)
    meta = [
        {
            "type": "dataset",
            "cascade_volatiles": ["random", "timestamp"],
            "random": 1.0,
            "timestamp": 1.0,
            "label": "stable",
        }
    ]

    masked = dl._mask_volatiles(meta)

    assert masked == [
        {
            "type": "dataset",
            "cascade_volatiles": ["random", "timestamp"],
            "random": None,
            "timestamp": None,
            "label": "stable",
        }
    ]

    meta_without_volatiles = [{"label": "stable", "other": 3}]
    assert dl._mask_volatiles(meta_without_volatiles) == meta_without_volatiles
