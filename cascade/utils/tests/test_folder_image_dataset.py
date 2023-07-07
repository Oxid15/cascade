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

import os
import sys

import cv2
import numpy as np
import pytest

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.utils.vision import FolderImageDataset


@pytest.fixture
def image_folder(tmp_path):
    cv2.imwrite(os.path.join(tmp_path, "1.jpg"), np.zeros((4, 5, 3), dtype=np.uint8))
    cv2.imwrite(os.path.join(tmp_path, "2.png"), np.zeros((4, 5, 3), dtype=np.uint8))
    return tmp_path


@pytest.fixture
def not_image_folder(tmp_path):
    with open(os.path.join(tmp_path, "file.txt"), "w") as f:
        f.writelines(["hello"])
    return tmp_path


def test(image_folder):
    ds = FolderImageDataset(image_folder)

    assert len(ds) == 2
    assert ds[0].shape == (4, 5, 3)
    assert ds[1].shape == (4, 5, 3)


def test_raises(not_image_folder):
    ds = FolderImageDataset(not_image_folder)

    assert len(ds) == 1
    with pytest.raises(RuntimeError):
        ds[0]
