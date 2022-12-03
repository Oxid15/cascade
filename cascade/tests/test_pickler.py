"""
Copyright 2022 Ilia Moiseev
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
import datetime
import pytest
import pandas as pd

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import *
from cascade import utils as cdu


def f(x: int) -> int:
    return 2 * x


@pytest.mark.parametrize(
    'ds',
    [
        Iterator([0]),
        Wrapper([0]),
        ApplyModifier(Wrapper([0, 1, 2]), f),
        BruteforceCacher(Wrapper([0, 2])),
        Composer([Wrapper([0]), Wrapper([1])]),
        Concatenator([Wrapper([0]), Wrapper([1])]),
        CyclicSampler(Wrapper([0]), 1),
        RandomSampler(Wrapper([1, 2, 3]), 2),
        RangeSampler(Wrapper([0, 1, 2, 3]), 0, 3, 1),
        SequentialCacher(Wrapper([0, 1, 2, 3]))
    ]
)
def test_data_coverage(ds, tmp_path):
    Pickler(os.path.join(tmp_path, 'ds.pkl'), ds)


@pytest.mark.parametrize(
    'ds',
    [
        cdu.TableDataset(t=pd.DataFrame()),
        cdu.TableFilter(cdu.TableDataset(t=pd.DataFrame()), []),
        cdu.TimeSeriesDataset(time=[datetime.datetime(2022, 12, 2)], data=[24])
    ]
)
def test_utils_coverage(ds, tmp_path):
    Pickler(os.path.join(tmp_path, 'ds.pkl'), ds)


@pytest.mark.parametrize(
    'ds',
    [
        Wrapper([1, 2, 3, 4, 5]),
        Wrapper([1]),
        Sampler(Modifier(Wrapper([1])), 1)
    ]
)
def test_integrity(ds, tmp_path):
    _ = Pickler(os.path.join(tmp_path, 'ds.pkl'), ds)
    loaded_ds = Pickler(os.path.join(tmp_path, 'ds.pkl'))

    true = []
    for i in range(len(ds)):
        true.append(ds[i])

    res = []
    for i in range(len(loaded_ds)):
        res.append(loaded_ds[i])

    assert res == true

    assert type(loaded_ds.ds()) == type(ds)
    assert str(loaded_ds.ds()) == str(ds)
