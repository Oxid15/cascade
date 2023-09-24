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
import shutil
import sys

import pytest
from sklearn import metrics

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.models import BasicModel
from cascade.utils.sklearn import SkMetric


def test():
    model = BasicModel()
    model.predict = lambda x: [0 for _ in range(len(x))]

    x = [None for _ in range(5)]
    gt = [0, 0, 0, 1, 1]
    model.evaluate(x, gt, metrics=[
        SkMetric("acc"),
        SkMetric("accuracy_score")
    ])

    assert model.metrics[0].value == 3 / 5
    assert model.metrics[1].value == 3 / 5

    pred = model.predict(x)
    assert metrics.accuracy_score(gt, pred) == 3 / 5
