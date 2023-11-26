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

import json
import os
import sys

# import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler, JSONEncoder
from cascade.metrics import Accuracy


def test_save_load(tmp_path_str):
    metric = Accuracy(2 / 3)

    metric_2 = Accuracy()
    metric_2.compute([0, 0, 0], [0, 0, 1])

    metric_3 = Accuracy()
    metric_3.compute_add([0], [0])
    metric_3.compute_add([0], [0])
    metric_3.compute_add([0], [1])

    assert metric.value == metric_2.value
    assert metric.value == metric_3.value

    MetaHandler.write(os.path.join(tmp_path_str, "metric.json"), metric)

    from_file = MetaHandler.read(os.path.join(tmp_path_str, "metric.json"))

    # This accounts for type changes for example dates
    assert json.loads(JSONEncoder().encode(metric.to_dict())) == from_file
