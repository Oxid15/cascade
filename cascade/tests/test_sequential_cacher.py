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

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.data import SequentialCacher


def test(number_dataset):
    ds = SequentialCacher(number_dataset, 2)
    res = []
    for i in range(len(ds)):
        res.append(ds[i])
    assert res == [item for item in number_dataset]


def test_repeated_usage(number_dataset):
    ds = SequentialCacher(number_dataset, 2)
    res = []
    for i in range(len(ds)):
        res.append(ds[i])

    assert res == [item for item in number_dataset]

    res = []
    for i in range(len(ds)):
        res.append(ds[i])

    assert res == [item for item in number_dataset]
