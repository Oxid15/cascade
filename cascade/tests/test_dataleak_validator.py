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
import pytest
import numpy as np

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

import cascade.data as cdd
from cascade import meta as cme


def test_simple_hash():
    train_ds = cdd.Wrapper(['a', 'b', 'c'])
    test_ds = cdd.Wrapper(['d', 'e', 'f'])

    cme.DataleakValidator(train_ds, test_ds)

    train_ds = cdd.Wrapper(['a', 'b', 'c'])
    test_ds = cdd.Wrapper(['c', 'd', 'e'])

    with pytest.raises(cme.DataValidationException):
        cme.DataleakValidator(train_ds, test_ds)


def test_np_hash():
    train_ds = cdd.Wrapper(np.ones(10))
    test_ds = cdd.Wrapper(np.zeros(10))

    cme.DataleakValidator(train_ds, test_ds, hash_fn=cme.numpy_md5)

    train_ds = cdd.Wrapper(np.zeros(10))
    test_ds = cdd.Wrapper(np.zeros(10))

    with pytest.raises(cme.DataValidationException):
        cme.DataleakValidator(train_ds, test_ds, hash_fn=cme.numpy_md5)


def test_empty():
    train_ds = cdd.Wrapper([0, 1, 2, 3])
    test_ds = cdd.Wrapper([])

    cme.DataleakValidator(train_ds, test_ds)

    train_ds = cdd.Wrapper([])
    test_ds = cdd.Wrapper([0, 1, 2, 3])

    cme.DataleakValidator(train_ds, test_ds)
