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
import traceback

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import ApplyModifier, Dataset, GetItemException, Wrapper


class RaiseDataset(Dataset):
    def get(self, index):
        raise RuntimeError("on no!")

    def __len__(self):
        return 1


class FailingModifier(ApplyModifier):
    def __init__(self, dataset, fail_indices=None, *args, **kwargs):
        super().__init__(dataset, lambda x: x, *args, **kwargs)
        self.fail_indices = fail_indices or []

    def get(self, index):
        if index in self.fail_indices:
            raise ValueError(f"Intentional failure at index {index}")
        return super().get(index)


def test_dataset_get_success():
    data = [1, 2, 3, 4, 5]
    ds = Wrapper(data)

    for i, expected in enumerate(data):
        assert ds[i] == expected


def test_dataset_get_exception_wrapping():
    ds = RaiseDataset()

    with pytest.raises(GetItemException) as exc_info:
        ds[0]

    assert "RaiseDataset" in str(exc_info.value)
    assert "index 0" in str(exc_info.value)

    assert isinstance(exc_info.value.__cause__, RuntimeError)
    assert str(exc_info.value.__cause__) == "on no!"


def test_dataset_get_exception_with_different_index_types():
    ds = RaiseDataset()

    with pytest.raises(GetItemException) as exc_info:
        ds["some_key"]
    assert "index some_key" in str(exc_info.value)

    with pytest.raises(GetItemException) as exc_info:
        ds[(0, 1)]
    assert "index (0, 1)" in str(exc_info.value)


def test_dataset_get_vs_getitem():
    data = ["a", "b", "c"]
    ds = Wrapper(data)

    for i in range(len(data)):
        assert ds.get(i) == ds[i]


def test_pipeline_get_pipelines():
    data = [1, 2, 3, 4, 5]
    ds = Wrapper(data)

    ds = FailingModifier(ds, fail_indices=[1])
    ds = FailingModifier(ds, fail_indices=[3])
    ds = ApplyModifier(ds, lambda x: x * 2)

    with pytest.raises(GetItemException) as exc_info:
        ds[1]

    assert "ApplyModifier" in str(exc_info.value)
    assert "index 1" in str(exc_info.value)
    tb_str = "".join(
        traceback.format_exception(
            type(exc_info.value), exc_info.value, exc_info.value.__traceback__
        )
    )
    assert "Intentional failure at index 1" in tb_str

    with pytest.raises(GetItemException) as exc_info:
        ds[3]

    assert "ApplyModifier" in str(exc_info.value)
    assert "index 3" in str(exc_info.value)
    tb_str = "".join(
        traceback.format_exception(
            type(exc_info.value), exc_info.value, exc_info.value.__traceback__
        )
    )
    assert "Intentional failure at index 3" in tb_str

    assert ds[0] == 2
    assert ds[2] == 6
    assert ds[4] == 10
