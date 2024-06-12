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
from typing import List, Tuple

import pydantic
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Dataset, SchemaModifier, ValidationError


class FiveIdenticalImages(Dataset):
    def __getitem__(self, idx):
        return AnnotImage(
            image=[[[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]],
            segments=[[0, 1, 2], [0, 1, 2]],
            bboxes=[(0, 0, 1, 1)],
        )

    def __len__(self):
        return 5


class AnnotImage(pydantic.BaseModel):
    image: List[List[List[float]]]
    segments: List[List[int]]
    bboxes: List[Tuple[int, int, int, int]]


class ImagesDataset(SchemaModifier):
    in_schema = AnnotImage


class IDoNothing(ImagesDataset):
    def __getitem__(self, idx):
        item = self._dataset[idx]
        return item


def test_wrapper():
    ds = FiveIdenticalImages()
    ds = IDoNothing(ds)

    meta = ds.get_meta()

    assert len(meta) == 3
    assert "in_schema" in meta[0]
    assert isinstance(meta[0]["in_schema"], dict)
    assert meta[1]["name"].split(".")[-1] == "ValidationWrapper"


def test_correct_schema():
    ds = FiveIdenticalImages()
    ds = IDoNothing(ds)

    item = ds[0]
    assert isinstance(item.image, list)
    assert isinstance(item.segments, list)
    assert isinstance(item.bboxes, list)


class BrokenImage(pydantic.BaseModel):
    image: List[List[float]]
    segments: List[str]


class FiveBrokenImageDataset(Dataset):
    def __getitem__(self, index: int):
        return BrokenImage(image=[[0.]], segments=["lol"])

    def __len__(self) -> int:
        return 5


def test_wrong_schema():
    ds = FiveBrokenImageDataset()
    ds = IDoNothing(ds)

    with pytest.raises(ValidationError) as e:
        item = ds[0]
    assert e.value.error_index == 0
