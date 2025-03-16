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

# import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import JSONEncoder, MetaHandler
from cascade.metrics import Metric


def test_save_load(tmp_path_str):
    metric = Metric(
        name="acc",
        value=0.48,
        dataset="mnist",
        split="train",
        direction="up",
        interval=(0.46, 0.50),
        extra={"weighted_acc": 0.32}
    )

    MetaHandler.write(os.path.join(tmp_path_str, "metric.json"), metric)

    from_file = MetaHandler.read(os.path.join(tmp_path_str, "metric.json"))
    assert JSONEncoder().obj_to_dict(metric.to_dict()) == from_file
