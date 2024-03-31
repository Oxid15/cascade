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

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

import pandas as pd

from cascade.utils.tables import FeatureTable


@pytest.fixture
def ft():
    df = pd.DataFrame([[1, 3], [2, 4], [3, 5]], columns=["a", "b"])
    ft = FeatureTable(df)
    ft.add_feature("c", lambda df: df["a"] + df["b"])
    return ft


def test_add_feature(ft):
    names = ft.get_features()
    assert names == ["a", "b", "c"]


def test_function(ft):
    cdf = ft.get_table()
    assert cdf["c"].tolist() == [4, 6, 8]


def test_get_subset(ft):
    df = ft.get_table(["a", "b"])
    assert list(df.columns) == ["a", "b"]
