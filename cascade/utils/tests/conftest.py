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

import pytest
import datetime
from cascade import utils as cdu
from cascade.data import Dataset

import pandas as pd


@pytest.fixture(
    params=[
        cdu.TableDataset(t=pd.DataFrame([[1, 2, 3]])),
        cdu.TableFilter(cdu.TableDataset(t=pd.DataFrame([[1, 2, 3]])), [False, True, False]),
        cdu.TimeSeriesDataset(time=[datetime.datetime(2022, 12, 2)], data=[24])
    ]
)
def utils_dataset(request) -> Dataset:
    return request.param
