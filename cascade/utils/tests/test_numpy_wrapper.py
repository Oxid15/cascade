"""
Copyright 2022-2025 Ilia Moiseev

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

import numpy as np
import pytest

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.utils.numpy_wrapper import NumpyWrapper


@pytest.mark.skip
def test(tmp_path):
    arr = np.array([1, 2, 3, 4, 5])
    path = os.path.join(tmp_path, "arr.npy")
    np.save(path, arr)

    ds = NumpyWrapper(path)
    assert arr.tolist() == [item for item in ds]
