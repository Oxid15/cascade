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
import os
import sys

import pandas as pd
import pytest

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import Dataset, Wrapper
from cascade.utils.samplers import OverSampler, UnderSampler, WeighedSampler
from cascade.utils.tables import TableDataset, TableFilter
from cascade.utils.time_series import TimeSeriesDataset


@pytest.fixture(
    params=[
        TableDataset(t=pd.DataFrame([[1, 2, 3]])),
        TableFilter(TableDataset(t=pd.DataFrame([[1, 2, 3]])), [0, 1, 0]),
        TimeSeriesDataset(time=[datetime.datetime(2022, 12, 2)], data=[24]),
        OverSampler(Wrapper([(0, 0), (0, 0), (0, 1), (0, 0)])),
        UnderSampler(Wrapper([(0, 0), (0, 0), (0, 1), (0, 0)])),
        WeighedSampler(Wrapper([(0, 0), (0, 0), (0, 1), (0, 0)]), {0: 1}),
        WeighedSampler(Wrapper([(0, 0), (0, 0), (0, 1), (0, 0)]), {0: 1, 1: 2}),
        WeighedSampler(Wrapper([(0, 0), (0, 0), (0, 1), (0, 0)])),
    ]
)
def utils_dataset(request) -> Dataset:
    return request.param
